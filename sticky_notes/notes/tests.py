# notes/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import Note, Author
from django.utils.timezone import now


class NoteModelTest(TestCase):
    """This test class works to ensure that a note
    populates correctly, including the title, content,
    and date time."""
    def setUp(self):
        """Creates the Note and Author objects for testing"""
        author = Author.objects.create(name='Test Author')
        Note.objects.create(title='Test Note', content='This is a test note.',
                            author=author)

    def test_note_has_title(self):
        """Tests that a Note object has the expected title"""
        note = Note.objects.get(id=1)
        self.assertEqual(note.title, 'Test Note')

    def test_note_has_content(self):
        """Tests that the note content populates correctly"""
        note = Note.objects.get(id=1)
        self.assertEqual(note.content, 'This is a test note.')

    def test_note_has_date(self):
        """Test that ensures a Note object has the date/time
        listed correctly"""
        note = Note.objects.get(id=1)
        current_time = now()

        self.assertAlmostEqual(
            note.created_at.timestamp(),
            current_time.timestamp(),
            delta=1,
            msg=f"created_at {note.created_at} is too far from {current_time}"
        )


class NoteViewTest(TestCase):
    """This test class tests the functionality of the note
    list view on a user's dashboard."""
    def setUp(self):
        """Creates an Author object and a test note."""
        author = Author.objects.create(name='Test Author')
        Note.objects.create(title='Test Note', content='This is a test note.',
                            author=author)

    def test_note_list_view(self):
        """Testing the list view functionality"""
        response = self.client.get(reverse('note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Note')

    def test_note_detail_view(self):
        """Test for the detail view functionality"""
        note = Note.objects.get(id=1)
        response = self.client.get(reverse('note_detail',
                                           args=[str(note.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Note')
        self.assertContains(response, 'This is a test note.')
