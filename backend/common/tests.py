from datetime import timedelta
from io import BytesIO
from unittest.mock import patch, MagicMock
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.db.models.query import QuerySet
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
        storage.return_value.upload_fileobj.assert_called_once()
        photo_id = response.data['id']
        storage.return_value.get_object.return_value = {'Body': BytesIO(data.getvalue())}
        content = self.client.get(f'/api/photos/{photo_id}/content/')
        self.assertEqual(content.status_code, 200)
        self.assertEqual(b''.join(content.streaming_content), data.getvalue())
        self.auth(self.other)
        self.assertEqual(self.client.get(f'/api/photos/{photo_id}/content/').status_code, 400)
        self.auth(self.alice)
        self.assertEqual(self.client.delete(f'/api/photos/{photo_id}/').status_code, 204)
        storage.return_value.delete_object.assert_called_once()
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
