from datetime import timedelta
from io import BytesIO
from unittest.mock import patch, MagicMock
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
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
    def pair(self):
        self.auth(self.alice)
        response = self.client.post('/api/couple-invitations/')
        self.assertEqual(response.status_code, 201)
        code = response.data['code']
        self.auth(self.bob)
        self.assertEqual(self.client.post('/api/couple-invitations/accept/', {'code': code}).status_code, 200)
        return code
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
    def test_invite_self_expired_and_reuse(self):
        self.auth(self.alice)
        invitation = Invitation.objects.create(sender=self.alice)
        self.assertEqual(self.client.post('/api/couple-invitations/accept/', {'code': invitation.code}).status_code, 400)
        invitation.expires_at = timezone.now() - timedelta(seconds=1)
        invitation.save()
        self.auth(self.bob)
        self.assertEqual(self.client.post('/api/couple-invitations/accept/', {'code': invitation.code}).status_code, 400)
        code = self.pair()
        self.auth(self.other)
        self.assertEqual(self.client.post('/api/couple-invitations/accept/', {'code': code}).status_code, 400)
        self.assertEqual(Membership.objects.count(), 2)
    def test_partner_access_comments_and_reactions(self):
        memory = self.setup_memory()
        self.auth(self.alice)
        self.assertEqual(self.client.get(f'/api/memories/{memory.pk}/').status_code, 200)
        self.assertEqual(self.client.post(f'/api/memories/{memory.pk}/comment/', {'text': 'Đẹp quá!'}).status_code, 201)
        self.assertTrue(self.client.post(f'/api/memories/{memory.pk}/react/').data['liked'])
        self.assertFalse(self.client.post(f'/api/memories/{memory.pk}/react/').data['liked'])
        self.assertEqual(self.client.get(f'/api/memories/{memory.pk}/').data['comments'][0]['author_name'], 'Alice')
    def test_other_couple_cannot_read_write_or_move_memory(self):
        memory = self.setup_memory()
        third = User.objects.create_user(username='third', password='Str0ng-pass!')
        self.auth(self.other)
        code = self.client.post('/api/couple-invitations/').data['code']
        self.auth(third)
        self.client.post('/api/couple-invitations/accept/', {'code': code})
        self.assertEqual(self.client.get('/api/memories/').data, [])
        self.assertEqual(self.client.get(f'/api/memories/{memory.pk}/').status_code, 404)
        self.assertEqual(self.client.post('/api/memories/', {'jar': memory.jar_id, 'title': 'intrusion', 'date': '2026-11-15'}).status_code, 400)
        foreign_jar = Jar.objects.create(cabinet=Cabinet.objects.exclude(pk=memory.jar.cabinet_id).get(), name='Other')
        self.auth(self.alice)
        self.assertEqual(self.client.patch(f'/api/memories/{memory.pk}/', {'jar': foreign_jar.pk}).status_code, 400)
        self.assertEqual(self.client.patch(f'/api/memories/{memory.pk}/', {'title': 'Edited'}).status_code, 200)
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
    def test_anonymous_denied(self):
        for endpoint in ['couples/', 'cabinets/', 'jars/', 'memories/', 'users/me/']:
            self.assertEqual(self.client.get('/api/' + endpoint).status_code, 401)
