from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from organizations.models import Organization
from ingestion.models import Event, APIKey


class EventIngestionBasicValidationTests(TestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Org"
        )

        self.other_organization = Organization.objects.create(
            name="Other Org"
        )

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.organization,
            role="owner",
        )

    def test_user_belongs_to_organization(self):
        self.assertEqual(
            self.user.organization,
            self.organization
        )

        self.assertEqual(
            self.user.role,
            "owner"
        )

    def test_event_creation(self):
        event = Event.objects.create(
            organization=self.organization,
            event_name="user_signup",
            payload={
                "user_id": 1,
                "source": "test"
            },
            source_type=Event.SOURCE_API,
            occurred_at=timezone.now(),
        )

        self.assertEqual(
            Event.objects.count(),
            1
        )

        self.assertEqual(
            event.organization,
            self.organization
        )

        self.assertEqual(
            event.event_name,
            "user_signup"
        )

    def test_batch_event_creation(self):
        events = [
            Event(
                organization=self.organization,
                event_name="purchase",
                payload={
                    "amount": 100
                },
                source_type=Event.SOURCE_BATCH,
                occurred_at=timezone.now(),
            ),
            Event(
                organization=self.organization,
                event_name="login",
                payload={
                    "device": "mobile"
                },
                source_type=Event.SOURCE_BATCH,
                occurred_at=timezone.now(),
            ),
        ]

        Event.objects.bulk_create(events)

        self.assertEqual(
            Event.objects.filter(
                organization=self.organization
            ).count(),
            2
        )

    def test_organization_data_isolation(self):
        Event.objects.create(
            organization=self.other_organization,
            event_name="hidden_event",
            payload={
                "secret": True
            },
            source_type=Event.SOURCE_API,
            occurred_at=timezone.now(),
        )

        Event.objects.create(
            organization=self.organization,
            event_name="visible_event",
            payload={
                "ok": True
            },
            source_type=Event.SOURCE_API,
            occurred_at=timezone.now(),
        )

        own_events = Event.objects.filter(
            organization=self.organization
        )

        self.assertEqual(
            own_events.count(),
            1
        )

        self.assertEqual(
            own_events.first().event_name,
            "visible_event"
        )

    def test_api_key_creation(self):
        api_key = APIKey.objects.create(
            organization=self.organization,
            name="Test API Key",
            created_by=self.user,
        )

        self.assertEqual(
            api_key.organization,
            self.organization
        )

        self.assertTrue(
            api_key.is_active
        )