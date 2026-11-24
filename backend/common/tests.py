from datetime import timedelta
from io import BytesIO, StringIO
from unittest.mock import ANY, patch, MagicMock
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.db.models.query import QuerySet
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from users.models import User
from couples.models import Membership
from couple_invitations.models import Invitation
from cabinets.models import Cabinet
from jars.models import Jar
from memories.models import Memory
from photos.models import Photo

class WorkflowTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='Str0ng-pass!', display_name='Alice')
        self.bob = User.objects.create_user(username='bob', password='Str0ng-pass!', display_name='Bob')
        self.other = User.objects.create_user(username='other', password='Str0ng-pass!', display_name='Other')
    def auth(self, user):
        self.client.force_authenticate(user)
    def invite(self, sender, recipient):
        self.auth(sender)
        response = self.client.post('/api/couple-invitations/', {'tag': recipient.tag})
        self.assertEqual(response.status_code, 201)
        return response.data['id']
    def accept(self, user, invitation_id):
        self.auth(user)
        return self.client.post(f'/api/couple-invitations/{invitation_id}/accept/')
    def pair(self):
        invitation_id = self.invite(self.alice, self.bob)
        self.assertEqual(self.accept(self.bob, invitation_id).status_code, 200)
        return invitation_id
    def setup_memory(self):
        self.pair()
        cabinet = Cabinet.objects.get()
        response = self.client.post('/api/jars/', {'cabinet': cabinet.pk, 'name': 'Hẹn hò'})
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/memories/', {'jar': response.data['id'], 'title': 'Cà phê', 'date': '2026-11-15'})
        self.assertEqual(response.status_code, 201)
        return Memory.objects.get()
    @patch('photos.services.storage')
    def test_partner_can_delete_memory_the_other_created(self, storage):
        memory = self.setup_memory()
        partner = self.bob if memory.author == self.alice else self.alice
        self.auth(partner)
        self.assertEqual(self.client.delete(f'/api/memories/{memory.pk}/').status_code, 204)
        self.assertFalse(Memory.objects.exists())
    def test_partner_can_add_memory_to_jar_the_other_created(self):
        memory = self.setup_memory()  # jar and first memory created by Bob
        self.auth(self.alice)
        response = self.client.post('/api/memories/', {'jar': memory.jar_id, 'title': 'Trà sữa', 'date': '2026-11-16'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], self.alice.pk)
    def test_one_cabinet_per_couple_and_year(self):
        self.pair()
        existing = Cabinet.objects.get()
        self.auth(self.alice)  # Alice's app did not know the cabinet exists yet
        response = self.client.post('/api/cabinets/', {'name': 'Tủ thương', 'year': existing.year})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], existing.pk)
        self.assertEqual(Cabinet.objects.count(), 1)
        other_year = self.client.post('/api/cabinets/', {'name': 'Tủ thương', 'year': existing.year + 1}).data['id']
        response = self.client.patch(f'/api/cabinets/{other_year}/', {'year': existing.year})
        self.assertEqual(response.status_code, 400)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cabinet.objects.create(couple=existing.couple, name='Trùng', year=existing.year)
    def test_registration_login_logout(self):
        response = self.client.post('/api/auth/register/', {'username': 'new', 'password': 'secure-l0ng-password', 'display_name': 'Minh'})
        self.assertEqual(response.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
        self.assertEqual(self.client.get('/api/users/me/').status_code, 200)
        self.assertEqual(self.client.post('/api/auth/logout/').status_code, 204)
        self.assertEqual(self.client.get('/api/users/me/').status_code, 401)
    def test_user_tag_generated_and_exposed(self):
        self.assertRegex(self.alice.tag, r'^#[A-Z0-9]{8}$')
        self.assertRegex(self.alice.tag[1:], r'[A-Z]')
        self.assertRegex(self.alice.tag[1:], r'[0-9]')
        self.assertEqual(len({self.alice.tag, self.bob.tag, self.other.tag}), 3)
        self.auth(self.alice)
        self.assertEqual(self.client.get('/api/users/me/').data['tag'], self.alice.tag)
        self.client.patch('/api/users/me/', {'tag': '#AAAA1111'})
        self.alice.refresh_from_db()
        self.assertNotEqual(self.alice.tag, '#AAAA1111')
    def test_invite_by_tag_validation(self):
        self.auth(self.alice)
        self.assertEqual(self.client.post('/api/couple-invitations/', {'tag': self.alice.tag}).status_code, 400)
        self.assertEqual(self.client.post('/api/couple-invitations/', {'tag': '#NOPE0000'}).status_code, 400)
        # Tag is accepted without '#' and in lowercase.
        response = self.client.post('/api/couple-invitations/', {'tag': self.bob.tag[1:].lower()})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['recipient']['tag'], self.bob.tag)
        # Re-inviting the same person returns the pending invitation.
        self.assertEqual(self.client.post('/api/couple-invitations/', {'tag': self.bob.tag}).data['id'], response.data['id'])
        self.auth(self.bob)
        listing = self.client.get('/api/couple-invitations/').data
        self.assertEqual([i['sender']['tag'] for i in listing['received']], [self.alice.tag])
        self.assertEqual(listing['sent'], [])
    def test_accept_rules(self):
        invitation_id = self.invite(self.alice, self.bob)
        # Only the recipient can accept.
        self.assertEqual(self.accept(self.alice, invitation_id).status_code, 404)
        self.assertEqual(self.accept(self.other, invitation_id).status_code, 404)
        Invitation.objects.filter(pk=invitation_id).update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.accept(self.bob, invitation_id).status_code, 400)
        invitation_id = self.pair()
        self.assertEqual(self.accept(self.bob, invitation_id).status_code, 400)
        self.auth(self.other)
        self.assertEqual(self.client.post('/api/couple-invitations/', {'tag': self.alice.tag}).status_code, 400)
        self.assertEqual(Membership.objects.count(), 2)
    def test_tag_regenerated_when_already_taken(self):
        with patch('users.models.generate_tag', side_effect=['#ZZZZ9999']):
            user = User(username='dup', tag=self.alice.tag)
            user.save()
        self.assertEqual(user.tag, '#ZZZZ9999')
    def test_tag_retried_when_taken_concurrently(self):
        # Simulate another signup claiming the tag between the existence check and the insert.
        real_exists, calls = QuerySet.exists, []
        def racy_exists(qs):
            calls.append(qs)
            return False if len(calls) == 1 else real_exists(qs)
        with patch.object(QuerySet, 'exists', autospec=True, side_effect=racy_exists), patch('users.models.generate_tag', side_effect=['#YYYY8888']):
            user = User(username='racer', tag=self.alice.tag)
            user.save()
        self.assertEqual(user.tag, '#YYYY8888')
        self.assertEqual(User.objects.filter(tag=self.alice.tag).count(), 1)
    def test_other_integrity_errors_not_swallowed(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(username='alice', password='x')
    def test_decline(self):
        invitation_id = self.invite(self.alice, self.bob)
        self.auth(self.other)
        self.assertEqual(self.client.post(f'/api/couple-invitations/{invitation_id}/decline/').status_code, 404)
        self.auth(self.bob)
        self.assertEqual(self.client.post(f'/api/couple-invitations/{invitation_id}/decline/').status_code, 204)
        self.assertEqual(self.client.get('/api/couple-invitations/').data['received'], [])
        self.assertEqual(self.accept(self.bob, invitation_id).status_code, 400)
        self.assertEqual(self.client.post(f'/api/couple-invitations/{invitation_id}/decline/').status_code, 400)
        self.auth(self.alice)
        self.assertEqual(self.client.get('/api/couple-invitations/').data['sent'], [])
        # The sender can invite again after a decline.
        self.assertNotEqual(self.invite(self.alice, self.bob), invitation_id)
        self.assertFalse(Membership.objects.exists())
    def test_partner_access_comments_and_reactions(self):
        memory = self.setup_memory()
        self.auth(self.alice)
        self.assertEqual(self.client.get(f'/api/memories/{memory.pk}/').status_code, 200)
        self.assertEqual(self.client.post(f'/api/memories/{memory.pk}/comment/', {'text': 'Đẹp quá!'}).status_code, 201)
        self.assertTrue(self.client.post(f'/api/memories/{memory.pk}/react/').data['liked'])
        self.assertFalse(self.client.post(f'/api/memories/{memory.pk}/react/').data['liked'])
        self.assertEqual(self.client.get(f'/api/memories/{memory.pk}/').data['comments'][0]['author_name'], 'Alice')
        data = self.client.get(f'/api/memories/{memory.pk}/').data
        self.assertEqual((data['author'], data['comments'][0]['author']), (self.bob.pk, self.alice.pk))
        self.assertIn('created_at', data)
    def test_other_couple_cannot_read_write_or_move_memory(self):
        memory = self.setup_memory()
        third = User.objects.create_user(username='third', password='Str0ng-pass!')
        self.accept(third, self.invite(self.other, third))
        self.assertEqual(self.client.get('/api/memories/').data, [])
        self.assertEqual(self.client.get(f'/api/memories/{memory.pk}/').status_code, 404)
        self.assertEqual(self.client.post('/api/memories/', {'jar': memory.jar_id, 'title': 'intrusion', 'date': '2026-11-15'}).status_code, 400)
        foreign_jar = Jar.objects.create(cabinet=Cabinet.objects.exclude(pk=memory.jar.cabinet_id).get(), name='Other')
        self.auth(self.alice)
        self.assertEqual(self.client.patch(f'/api/memories/{memory.pk}/', {'jar': foreign_jar.pk}).status_code, 400)
        self.assertEqual(self.client.patch(f'/api/memories/{memory.pk}/', {'title': 'Edited'}).status_code, 200)
        self.assertEqual(self.client.patch(f'/api/memories/{memory.pk}/', {'author': self.alice.pk}).status_code, 200)
        memory.refresh_from_db()
        self.assertEqual(memory.author, self.bob)
    @patch('photos.services.storage')
    def test_photo_upload_validation_and_privacy(self, storage):
        memory = self.setup_memory()
        response = self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('bad.png', b'not an image', content_type='image/png')}, format='multipart')
        self.assertEqual(response.status_code, 400)
        data = BytesIO()
        Image.new('RGB', (8,8)).save(data, format='PNG')
        response = self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('photo.png', data.getvalue(), content_type='image/png')}, format='multipart')
        self.assertEqual(response.status_code, 201)
        uploaded = [c.args[2] for c in storage.return_value.upload_fileobj.call_args_list]
        photo_id = response.data['id']
        key = Photo.objects.get(pk=photo_id).object_key
        self.assertRegex(key, rf'^{memory.jar_id}/{memory.pk}/[0-9a-f]{{32}}\.png$')
        base = key.rsplit('.', 1)[0]
        self.assertEqual(uploaded, [key, base + '.thumb.jpg', base + '.display.jpg'])  # original + smaller copies
        thumb, display = (Image.open(c.args[0]) for c in storage.return_value.upload_fileobj.call_args_list[1:])
        self.assertEqual((thumb.format, display.format), ('JPEG', 'JPEG'))
        # Three sizes through the authenticated API.
        self.assertEqual((response.data['url'], response.data['thumb_url'], response.data['display_url']),
                         (f'/api/photos/{photo_id}/content/', f'/api/photos/{photo_id}/content/?size=thumb', f'/api/photos/{photo_id}/content/?size=display'))
        other_jar = Jar.objects.create(cabinet=memory.jar.cabinet, name='Moved')
        self.assertEqual(self.client.patch(f'/api/memories/{memory.pk}/', {'jar': other_jar.pk}).status_code, 200)
        moved = Photo.objects.get(pk=photo_id).object_key
        self.assertEqual(moved, f'{other_jar.pk}/{memory.pk}/' + key.rsplit('/', 1)[-1])
        self.assertEqual(storage.return_value.copy_object.call_count, 3)  # the copies move with it
        self.assertEqual({c.kwargs['Key'] for c in storage.return_value.delete_object.call_args_list}, {key, base + '.thumb.jpg', base + '.display.jpg'})
        storage.return_value.delete_object.reset_mock()
        storage.return_value.get_object.return_value = {'Body': BytesIO(data.getvalue())}
        content = self.client.get(f'/api/photos/{photo_id}/content/')
        self.assertEqual(content.status_code, 200)
        self.assertEqual(b''.join(content.streaming_content), data.getvalue())
        self.assertEqual(content['Content-Type'], 'image/png')
        storage.return_value.get_object.return_value = {'Body': BytesIO(b'small')}
        thumb = self.client.get(f'/api/photos/{photo_id}/content/?size=thumb')
        self.assertEqual((thumb.status_code, thumb['Content-Type']), (200, 'image/jpeg'))
        self.assertEqual(storage.return_value.get_object.call_args.kwargs['Key'], moved.rsplit('.', 1)[0] + '.thumb.jpg')
        self.auth(self.other)
        self.assertEqual(self.client.get(f'/api/photos/{photo_id}/content/').status_code, 400)
        self.auth(self.alice)
        self.assertEqual(self.client.delete(f'/api/photos/{photo_id}/').status_code, 204)
        self.assertEqual(storage.return_value.delete_object.call_count, 3)
    @patch('photos.services.storage')
    def test_heic_upload_is_stored_as_jpeg(self, storage):
        memory = self.setup_memory()
        data = BytesIO()
        Image.new('RGB', (5000, 200), 'red').save(data, format='HEIF')
        response = self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('IMG_0001.HEIC', data.getvalue(), content_type='image/heic')}, format='multipart')
        self.assertEqual(response.status_code, 201)
        photo = Photo.objects.get(pk=response.data['id'])
        self.assertEqual(photo.content_type, 'image/jpeg')
        self.assertRegex(photo.object_key, r'\.jpg$')
        original, thumb, display = storage.return_value.upload_fileobj.call_args_list
        self.assertEqual(original.kwargs['ExtraArgs'], {'ContentType': 'image/jpeg'})
        self.assertEqual((Image.open(original.args[0]).format, Image.open(original.args[0]).width), ('JPEG', 4096))  # downscaled to MAX_SIDE
        self.assertEqual((Image.open(thumb.args[0]).width, Image.open(display.args[0]).width), (400, 1600))
    @patch('photos.services.storage')
    def test_iphone_mpo_jpeg_is_accepted(self, storage):  # JPEG + HDR gain map; Pillow reports MPO
        memory = self.setup_memory()
        data = BytesIO()
        Image.new('RGB', (64, 48), 'red').save(data, format='MPO', save_all=True, append_images=[Image.new('L', (32, 24))])
        self.assertEqual(Image.open(BytesIO(data.getvalue())).format, 'MPO')
        response = self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('IMG_2516.jpeg', data.getvalue(), content_type='image/jpeg')}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Photo.objects.get(pk=response.data['id']).content_type, 'image/jpeg')
    def test_memory_location_set_validated_and_cleared(self):
        memory = self.setup_memory()
        url = f'/api/memories/{memory.pk}/'
        response = self.client.patch(url, {'latitude': 11.940419, 'longitude': 108.458313, 'place': 'Hồ Xuân Hương, Đà Lạt'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.data['latitude'], response.data['place']), (11.940419, 'Hồ Xuân Hương, Đà Lạt'))
        self.assertEqual(self.client.patch(url, {'latitude': 91}, format='json').status_code, 400)  # out of range
        self.assertEqual(self.client.patch(url, {'longitude': None}, format='json').status_code, 400)  # half a pair
        self.auth(self.bob)  # the partner can move or clear the pin too
        response = self.client.patch(url, {'latitude': None, 'longitude': None}, format='json')
        self.assertEqual((response.status_code, response.data['latitude'], response.data['place']), (200, None, ''))
    @patch('memories.management.commands.backfill_locations.storage')
    def test_backfill_locations_from_photo_exif(self, storage):
        from django.core.management import call_command
        memory = self.setup_memory()
        def jpeg(gps=None):
            exif = Image.Exif()
            if gps:
                exif.get_ifd(0x8825).update(gps)
            data = BytesIO()
            Image.new('RGB', (8, 8)).save(data, format='JPEG', exif=exif)
            return data.getvalue()
        Photo.objects.create(memory=memory, object_key='a.jpg', content_type='image/jpeg')  # no GPS: next photo is used
        Photo.objects.create(memory=memory, object_key='b.jpg', content_type='image/jpeg')
        files = {'a.jpg': jpeg(), 'b.jpg': jpeg({1: 'N', 2: (11.0, 56.0, 25.5), 3: 'E', 4: (108.0, 27.0, 29.9)})}
        storage.return_value.get_object.side_effect = lambda Key, **kw: {'Body': BytesIO(files[Key])}
        call_command('backfill_locations', stdout=StringIO())
        memory.refresh_from_db()
        self.assertAlmostEqual(memory.latitude, 11.940417, places=5)
        self.assertAlmostEqual(memory.longitude, 108.458306, places=5)
        self.assertAlmostEqual(Photo.objects.get(object_key='b.jpg').latitude, 11.940417, places=5)  # the photo's own spot
        self.assertIsNone(Photo.objects.get(object_key='a.jpg').latitude)
    @patch('photos.services.storage')
    def test_memory_photos_keep_their_own_places(self, storage):
        # One memory, photos from two places: the browser sends each photo's GPS (read before it
        # re-encodes); without it the server reads the photo's own EXIF.
        memory = self.setup_memory()
        def jpeg(gps=None):
            exif = Image.Exif()
            if gps:
                exif.get_ifd(0x8825).update(gps)
            data = BytesIO()
            Image.new('RGB', (8, 8)).save(data, format='JPEG', exif=exif)
            return data.getvalue()
        sent = self.client.post('/api/photos/stage/', {'file': SimpleUploadedFile('a.jpg', jpeg(), content_type='image/jpeg'), 'latitude': 11.94, 'longitude': 108.45, 'place': 'Đà Lạt'}, format='multipart')
        exif = self.client.post('/api/photos/stage/', {'file': SimpleUploadedFile('b.jpg', jpeg({1: 'N', 2: (21.0, 1.0, 43.0), 3: 'E', 4: (105.0, 51.0, 8.0)}), content_type='image/jpeg')}, format='multipart')
        none = self.client.post('/api/photos/stage/', {'file': SimpleUploadedFile('c.jpg', jpeg(), content_type='image/jpeg')}, format='multipart')
        self.assertEqual(self.client.post('/api/photos/stage/', {'file': SimpleUploadedFile('d.jpg', jpeg(), content_type='image/jpeg'), 'latitude': 10}, format='multipart').status_code, 400)
        response = self.client.post('/api/memories/', {'jar': memory.jar_id, 'title': 'Xuyên Việt', 'date': '2026-11-20', 'staged_photos': [sent.data['token'], exif.data['token'], none.data['token']]}, format='json')
        self.assertEqual(response.status_code, 201)
        places = [(p['latitude'], p['longitude'], p['place']) for p in sorted(response.data['photos'], key=lambda p: p['id'])]
        self.assertEqual(places[0], (11.94, 108.45, 'Đà Lạt'))
        self.assertEqual((places[1][0], round(places[1][1], 4)), (21.028611, 105.8522))
        self.assertEqual(places[2], (None, None, ''))
        added = self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('e.jpg', jpeg(), content_type='image/jpeg'), 'latitude': 16.05, 'longitude': 108.2, 'place': 'Đà Nẵng'}, format='multipart')
        self.assertEqual((added.status_code, added.data['place']), (201, 'Đà Nẵng'))
    @patch('photos.management.commands.make_photo_variants.storage')
    def test_make_photo_variants_for_existing_photos(self, storage):
        from django.core.management import call_command
        memory = self.setup_memory()
        data = BytesIO()
        Image.new('RGB', (3000, 2000), 'green').save(data, format='JPEG')
        old = Photo.objects.create(memory=memory, object_key='1/1/old.jpg', content_type='image/jpeg')
        video = Photo.objects.create(memory=memory, object_key='1/1/clip.mp4', content_type='video/mp4')
        storage.return_value.get_object.return_value = {'Body': BytesIO(data.getvalue())}
        call_command('make_photo_variants', stdout=StringIO())
        old.refresh_from_db(); video.refresh_from_db()
        self.assertEqual((old.variants, video.variants), (True, False))  # videos have no copies
        keys = {c.args[2]: Image.open(c.args[0]).size for c in storage.return_value.upload_fileobj.call_args_list}
        self.assertEqual(keys, {'1/1/old.thumb.jpg': (400, 267), '1/1/old.display.jpg': (1600, 1067)})
    @patch('photos.services.storage')
    def test_memory_created_only_with_all_staged_photos(self, storage):
        self.pair()
        cabinet = Cabinet.objects.get()
        jar = self.client.post('/api/jars/', {'cabinet': cabinet.pk, 'name': 'Du lịch'}).data['id']
        data = BytesIO()
        Image.new('RGB', (8, 8)).save(data, format='PNG')
        tokens = []
        for i in range(2):
            response = self.client.post('/api/photos/stage/', {'file': SimpleUploadedFile(f'{i}.png', data.getvalue(), content_type='image/png')}, format='multipart')
            self.assertEqual(response.status_code, 201)
            tokens.append(response.data['token'])
        staged = [c.args[2] for c in storage.return_value.upload_fileobj.call_args_list]
        self.assertEqual(len(staged), 6)  # 2 photos x (original, thumb, display)
        self.assertTrue(all(k.startswith('staging/') for k in staged))
        self.assertFalse(Memory.objects.exists())  # nothing saved yet
        body = {'jar': jar, 'title': 'Đà Lạt', 'date': '2026-11-19', 'staged_photos': tokens}
        # A tampered token is rejected and no memory is created.
        response = self.client.post('/api/memories/', {**body, 'staged_photos': [tokens[0], tokens[1] + 'x']}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Memory.objects.exists())
        # Storage failing mid-way rolls the memory back and removes the copies made so far.
        storage.return_value.copy_object.side_effect = [None, RuntimeError('s3 down')]
        with self.assertRaises(RuntimeError):
            self.client.post('/api/memories/', body, format='json')
        self.assertFalse(Memory.objects.exists())
        self.assertFalse(Photo.objects.exists())
        self.assertEqual(storage.return_value.delete_object.call_count, 1)  # the one copy made before the failure
        storage.return_value.copy_object.side_effect = None
        storage.return_value.delete_object.reset_mock()
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post('/api/memories/', body, format='json')
        self.assertEqual(response.status_code, 201)
        memory = Memory.objects.get()
        self.assertEqual(len(response.data['photos']), 2)
        for photo in memory.photos.all():
            self.assertRegex(photo.object_key, rf'^{jar}/{memory.pk}/[0-9a-f]{{32}}\.png$')
        deleted = {c.kwargs['Key'] for c in storage.return_value.delete_object.call_args_list}
        self.assertEqual(deleted, set(staged))  # staged originals and copies removed after commit
        self.assertTrue(all(p.variants for p in memory.photos.all()))
        # Tokens are bound to the uploader.
        self.auth(self.other)
        self.assertEqual(self.client.post('/api/photos/stage/', {'file': SimpleUploadedFile('x.png', data.getvalue(), content_type='image/png')}, format='multipart').status_code, 400)  # not paired
    @patch('photos.services.storage')
    def test_video_upload_stream_and_delete(self, storage):
        from botocore.exceptions import ClientError
        memory = self.setup_memory()
        mp4 = b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom' + b'\x00' * 64
        mov = b'\x00\x00\x00\x14ftypqt  \x00\x00\x00\x00qt  ' + b'\x00' * 64
        for name, data, ctype, ext in [('clip.mp4', mp4, 'video/mp4', 'mp4'), ('IMG_0001.MOV', mov, 'video/quicktime', 'mov')]:
            response = self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile(name, data, content_type='application/octet-stream')}, format='multipart')
            self.assertEqual(response.status_code, 201, response.data)
            self.assertEqual(response.data['kind'], 'video')
            photo = Photo.objects.get(pk=response.data['id'])
            self.assertEqual(photo.content_type, ctype)
            self.assertTrue(photo.object_key.endswith('.' + ext))
            self.assertEqual(storage.return_value.upload_fileobj.call_args.kwargs['ExtraArgs'], {'ContentType': ctype})
        # Random bytes are still rejected; a HEIF brand is never mistaken for video.
        self.assertEqual(self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('x.mp4', b'not a video at all', content_type='video/mp4')}, format='multipart').status_code, 400)
        self.assertEqual(self.client.post('/api/photos/', {'memory': memory.pk, 'file': SimpleUploadedFile('x.heic', b'\x00\x00\x00\x18ftypheic' + b'\x00' * 40, content_type='image/heic')}, format='multipart').status_code, 400)
        # Streaming: signed link, Range support, no API token needed.
        url = self.client.get(f'/api/memories/{memory.pk}/').data['photos'][0]['stream_url']
        self.assertIn('/stream/?sig=', url)
        self.client.force_authenticate(None)
        body = MagicMock(); body.iter_chunks.return_value = [b'ab']
        storage.return_value.get_object.return_value = {'Body': body, 'ContentLength': 2, 'ContentRange': 'bytes 0-1/90'}
        response = self.client.get(url, HTTP_RANGE='bytes=0-1')
        self.assertEqual(response.status_code, 206)
        self.assertEqual((response['Content-Range'], response['Content-Length'], response['Accept-Ranges']), ('bytes 0-1/90', '2', 'bytes'))
        self.assertEqual(b''.join(response.streaming_content), b'ab')
        self.assertEqual(storage.return_value.get_object.call_args.kwargs['Range'], 'bytes=0-1')
        storage.return_value.get_object.return_value = {'Body': body, 'ContentLength': 90}
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertNotIn('Range', storage.return_value.get_object.call_args.kwargs)
        storage.return_value.get_object.side_effect = ClientError({'Error': {'Code': 'InvalidRange'}}, 'GetObject')
        self.assertEqual(self.client.get(url, HTTP_RANGE='bytes=999-').status_code, 416)
        storage.return_value.get_object.side_effect = None
        self.assertEqual(self.client.get(url.split('?')[0] + '?sig=forged').status_code, 403)
        image = Photo.objects.create(memory=memory, object_key='x/y/z.jpg', content_type='image/jpeg')
        from photos.services import stream_url
        self.assertEqual(self.client.get(stream_url(image)).status_code, 404)  # images aren't streamed
        # Either partner can delete a video.
        partner = self.bob if memory.author == self.alice else self.alice
        self.auth(partner)
        video_id = Photo.objects.filter(content_type__startswith='video/').first().pk
        self.assertEqual(self.client.delete(f'/api/photos/{video_id}/').status_code, 204)
        self.assertFalse(Photo.objects.filter(pk=video_id).exists())
    def test_couple_dates_validated(self):
        self.pair()
        url = f"/api/couples/{Membership.objects.get(user=self.bob).couple_id}/"
        response = self.client.patch(url, {'met_on': '2023-11-23', 'dating_since': '2024-02-14'}, format='json')
        self.assertEqual((response.status_code, response.data['met_on'], response.data['dating_since']), (200, '2023-11-23', '2024-02-14'))
        self.assertEqual(self.client.patch(url, {'dating_since': '2023-01-01'}, format='json').status_code, 400)  # before meeting
        future = (timezone.localdate() + timedelta(days=1)).isoformat()
        self.assertEqual(self.client.patch(url, {'met_on': future}, format='json').status_code, 400)
        self.auth(self.alice)  # either partner can change them
        self.assertEqual(self.client.patch(url, {'met_on': None}, format='json').data['met_on'], None)
    def test_quiz_ask_answer_points_and_streak(self):
        from couples.models import Couple
        from quizzes.models import Answer, Question
        from quizzes.services import streaks
        self.pair()
        self.auth(self.alice)
        bad = self.client.post('/api/quiz-questions/', {'text': 'Màu mình thích?', 'choices': ['Đỏ', 'đỏ'], 'correct': 0}, format='json')
        self.assertEqual(bad.status_code, 400)  # duplicate choices
        self.assertEqual(self.client.post('/api/quiz-questions/', {'text': 'Màu?', 'choices': ['Đỏ', 'Xanh'], 'correct': 2}, format='json').status_code, 400)
        q = self.client.post('/api/quiz-questions/', {'text': 'Màu mình thích?', 'choices': ['Đỏ', 'Xanh', 'Tím'], 'correct': 2}, format='json')
        self.assertEqual((q.status_code, q.data['author'], q.data['correct']), (201, self.alice.id, 2))
        url = f"/api/quiz-questions/{q.data['id']}/"
        self.assertEqual(self.client.post(url + 'answer/', {'choice': 2}, format='json').status_code, 403)  # not your own
        self.auth(self.bob)
        self.assertIsNone(self.client.get(url).data['correct'])  # hidden until answered
        self.assertEqual(self.client.delete(url).status_code, 403)  # only the author deletes
        response = self.client.post(url + 'answer/', {'choice': 1}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.data['question']['correct'], response.data['question']['answer']['correct'], response.data['points'], response.data['streak']), (2, False, 2, 1))
        self.assertEqual(self.client.post(url + 'answer/', {'choice': 2}, format='json').status_code, 400)  # only once
        couple = Couple.objects.get()
        self.assertEqual(couple.pet_points, 2)
        self.assertEqual(self.client.patch(f'/api/couples/{couple.pk}/', {'pet_points': 999}, format='json').data['pet_points'], 2)  # read-only
        self.auth(self.alice)
        self.assertEqual(self.client.delete(url).status_code, 400)  # answered: kept as history
        # Streak: days with any answer, by either partner.
        today = timezone.localdate()
        def answered(days_ago):
            question = Question.objects.create(couple=couple, author=self.alice, text='?', choices=['a', 'b'], correct=0)
            Answer.objects.create(question=question, user=self.bob, choice=0, answered_on=today - timedelta(days=days_ago))
        for days_ago in (1, 2, 5, 6, 7, 8):  # plus today's answer above
            answered(days_ago)
        self.assertEqual(streaks(couple), (3, 4))
        self.assertEqual(streaks(couple, today + timedelta(days=1)), (3, 4))  # still alive until the day ends
        self.assertEqual(streaks(couple, today + timedelta(days=2)), (0, 4))
        data = self.client.get('/api/couples/').data[0]
        self.assertEqual((data['quiz_streak'], data['quiz_max_streak']), (3, 4))
        self.auth(self.other)  # not in this couple: can't see or answer it
        self.assertIn(self.client.get(url).status_code, (400, 404))
        self.assertIn(self.client.post(url + 'answer/', {'choice': 0}, format='json').status_code, (400, 404))
    @patch('photos.services.storage')
    def test_avatar_upload_square_private_and_remove(self, storage):
        self.pair()
        self.auth(self.alice)
        data = BytesIO()
        Image.new('RGB', (1200, 800), 'blue').save(data, format='HEIF')  # any supported photo, here HEIC
        response = self.client.post('/api/users/me/avatar/', {'file': SimpleUploadedFile('me.heic', data.getvalue())}, format='multipart')
        self.assertEqual(response.status_code, 200)
        url = response.data['avatar_url']
        self.assertRegex(url, rf'^/api/users/{self.alice.id}/avatar/\?v=[0-9a-f]{{32}}$')
        fileobj, _, key = storage.return_value.upload_fileobj.call_args.args
        self.assertEqual(Image.open(fileobj).size, (512, 512))  # center-cropped square JPEG
        self.assertTrue(key.startswith(f'avatars/{self.alice.id}/'))
        bad = self.client.post('/api/users/me/avatar/', {'file': SimpleUploadedFile('x.png', b'not an image')}, format='multipart')
        self.assertEqual(bad.status_code, 400)
        storage.return_value.get_object.return_value = {'Body': BytesIO(b'jpeg-bytes')}
        self.auth(self.bob)  # the partner sees it (in the couple's member list too)
        self.assertEqual(self.client.get('/api/couples/').data[0]['members'][0]['avatar_url'] or self.client.get('/api/couples/').data[0]['members'][1]['avatar_url'], url)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.auth(self.other)  # nobody else does
        self.assertEqual(self.client.get(url).status_code, 404)
        self.auth(self.alice)  # back to the character art; the old file is deleted
        response = self.client.delete('/api/users/me/avatar/')
        self.assertIsNone(response.data['avatar_url'])
        storage.return_value.delete_object.assert_called_once_with(Bucket=ANY, Key=key)
    def test_shop_points_buy_and_theme(self):
        from couples.models import Couple
        memory = self.setup_memory()  # 1 memory = 10 points
        couple = Couple.objects.get()
        shop = self.client.get('/api/shop/').data
        self.assertEqual((shop['earned'], shop['spent'], shop['balance']), (10, 0, 10))
        self.assertEqual([(i['id'], i['price'], i['owned']) for i in shop['items']], [('theme_pink', 50, False)])
        self.assertEqual(self.client.post('/api/shop/theme_pink/buy/').status_code, 400)  # not enough points
        self.assertEqual(self.client.patch('/api/users/me/', {'theme': 'pink'}, format='json').status_code, 400)  # not owned
        couple.pet_points = 42  # e.g. 21 quiz answers
        couple.save()
        response = self.client.post('/api/shop/theme_pink/buy/')
        self.assertEqual((response.status_code, response.data['spent'], response.data['balance'], response.data['items'][0]['owned']), (201, 50, 2, True))
        self.assertEqual(self.client.post('/api/shop/theme_pink/buy/').status_code, 400)  # bought once per couple
        self.assertEqual(self.client.post('/api/shop/cat/buy/').status_code, 404)
        couple.refresh_from_db()
        self.assertEqual(couple.pet_points, 42)  # buying never takes points from the pet
        self.auth(self.bob)  # the partner owns it too and picks their own theme
        self.assertEqual(self.client.get('/api/shop/').data['balance'], 2)
        self.assertEqual(self.client.patch('/api/users/me/', {'theme': 'pink'}, format='json').data['theme'], 'pink')
        self.assertEqual(self.client.patch('/api/users/me/', {'theme': 'ocean'}, format='json').status_code, 400)
        self.auth(self.alice)
        self.assertEqual(self.client.get('/api/users/me/').data['theme'], '')
    def test_rename_pet_and_change_type(self):
        self.pair()
        couple_id = Membership.objects.get(user=self.alice).couple_id
        self.auth(self.alice)
        response = self.client.patch(f'/api/couples/{couple_id}/', {'pet_name': 'Mochi', 'pet_type': 'capybara'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.data['pet_name'], response.data['pet_type']), ('Mochi', 'capybara'))
        self.assertEqual(self.client.patch(f'/api/couples/{couple_id}/', {'pet_type': 'dragon'}).status_code, 400)
        self.assertEqual(self.client.patch(f'/api/couples/{couple_id}/', {'pet_name': '  '}, format='json').status_code, 400)
        self.assertEqual(self.client.get(f'/api/couples/{couple_id}/').data['pet_name'], 'Mochi')
        self.assertEqual(self.client.delete(f'/api/couples/{couple_id}/').status_code, 405)
        self.auth(self.other)
        self.assertEqual(self.client.patch(f'/api/couples/{couple_id}/', {'pet_name': 'Hacked'}).status_code, 404)
    def test_health_probes_skip_auth_and_throttling(self):
        for _ in range(70):  # more than the 60/hour anonymous limit
            self.assertEqual(self.client.get('/api/healthz/').status_code, 200)
        self.assertEqual(self.client.get('/api/readyz/').status_code, 200)
    def test_anonymous_denied(self):
        for endpoint in ['couples/', 'cabinets/', 'jars/', 'memories/', 'users/me/']:
            self.assertEqual(self.client.get('/api/' + endpoint).status_code, 401)

GOOGLE_CLAIMS = {'sub': '1234567890', 'email': 'An.Nguyen@gmail.com', 'email_verified': True, 'name': 'An Nguyễn'}

@override_settings(GOOGLE_CLIENT_ID='test-client.apps.googleusercontent.com')
class GoogleLoginTests(APITestCase):
    @patch('google.oauth2.id_token.verify_oauth2_token', return_value=GOOGLE_CLAIMS)
    def test_signup_then_login_with_same_google_account(self, verify):
        response = self.client.post('/api/auth/google/', {'credential': 'id-token'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['created'])
        self.assertEqual(response.data['user']['display_name'], 'An Nguyễn')
        self.assertEqual(verify.call_args.args[2], 'test-client.apps.googleusercontent.com')
        self.assertEqual(verify.call_args.kwargs['clock_skew_in_seconds'], 60)
        user = User.objects.get(google_sub='1234567890')
        self.assertEqual(user.email, 'an.nguyen@gmail.com')
        self.assertFalse(user.has_usable_password())
        again = self.client.post('/api/auth/google/', {'credential': 'id-token'})
        self.assertEqual(again.status_code, 200)
        self.assertFalse(again.data['created'])
        self.assertEqual(again.data['token'], response.data['token'])
        self.assertEqual(User.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {again.data["token"]}')
        self.assertEqual(self.client.get('/api/users/me/').data['id'], user.pk)

    @patch('google.oauth2.id_token.verify_oauth2_token', return_value=GOOGLE_CLAIMS)
    def test_username_collision_gets_suffix(self, verify):
        User.objects.create_user(username='an.nguyen@gmail.com', password='Str0ng-pass!', display_name='Someone')
        self.assertEqual(self.client.post('/api/auth/google/', {'credential': 'id-token'}).status_code, 201)
        self.assertTrue(User.objects.get(google_sub='1234567890').username.startswith('an.nguyen@gmail.com-'))

    @patch('google.oauth2.id_token.verify_oauth2_token', side_effect=ValueError('bad signature'))
    def test_invalid_token_rejected(self, verify):
        self.assertEqual(self.client.post('/api/auth/google/', {'credential': 'forged'}).status_code, 400)
        self.assertFalse(User.objects.exists())

    @patch('google.oauth2.id_token.verify_oauth2_token', return_value={**GOOGLE_CLAIMS, 'email_verified': False})
    def test_unverified_email_rejected(self, verify):
        self.assertEqual(self.client.post('/api/auth/google/', {'credential': 'id-token'}).status_code, 400)

    @override_settings(GOOGLE_CLIENT_ID='')
    def test_disabled_without_client_id(self):
        self.assertEqual(self.client.get('/api/auth/config/').data, {'google_client_id': '', 'version': 'dev'})
        self.assertEqual(self.client.post('/api/auth/google/', {'credential': 'id-token'}).status_code, 400)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_unreachable_returns_503(self, verify):
        from google.auth.exceptions import TransportError
        verify.side_effect = TransportError('connect timeout')
        self.assertEqual(self.client.post('/api/auth/google/', {'credential': 'id-token'}).status_code, 503)

    def test_config_exposes_client_id(self):
        self.assertEqual(self.client.get('/api/auth/config/').data, {'google_client_id': 'test-client.apps.googleusercontent.com', 'version': 'dev'})
