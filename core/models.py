import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.conf import settings # For AUTH_USER_MODEL

# User model
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='profile_imgs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Username is still required unless you customize it further.

    # User focus session stats
    focus_streak = models.IntegerField(default=0)
    longest_focus_streak = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0)
    # User preferences
    mins_for_streak = models.IntegerField(default=10)

    def get_short_name(self):
        return self.first_name

    def get_initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}" if self.last_name else f"{self.first_name[0]}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email


# Board models
class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    name = models.CharField(max_length=25, blank=False, null=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    favorite = models.BooleanField(default=False)
    color = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Board.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'boards'


class List(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            # New list, add it to the end
            max_position = List.objects.filter(board=self.board).aggregate(models.Max('position'))['position__max']
            self.position = (max_position or 0) + 1
        else:
            # Existing list, update positions if necessary
            old_position = List.objects.get(pk=self.pk).position
            if old_position != self.position:
                if old_position < self.position:
                    List.objects.filter(board=self.board, position__gt=old_position, position__lte=self.position).update(position=models.F('position') - 1)
                else:
                    List.objects.filter(board=self.board, position__lt=old_position, position__gte=self.position).update(position=models.F('position') + 1)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'lists'
        ordering = ['position']


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=30, blank=False, null=False)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    description = models.TextField(max_length=200, blank=True, null=True)
    image_url = models.CharField(blank=True, null=True, max_length=1000000)
    uploaded_img = models.ImageField(upload_to='card_images/', null=True, blank=True)
    priority = models.CharField(max_length=6, choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], default='', blank=True, null=True)
    due_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'cards'


class Subtask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    title = models.CharField(max_length=30, blank=False, null=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'subtasks'


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    text = models.TextField(max_length=200, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_reactions = models.IntegerField(default=0)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'comments'


class Reaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reaction_type


# models for focus session, focus streak
class FocusBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.TimeField(blank=True, null=True, default=None)
    description = models.TextField(max_length=200, blank=True, null=True)
    frequency_by_week = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'focus_block'


class FocusPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    blocks = models.ManyToManyField(FocusBlock, through="FocusBlockPath")
    total_time = models.PositiveIntegerField(blank=True, null=True)
    total_time_limit = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'focus_paths'


class FocusBlockPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.ForeignKey(FocusPath, on_delete=models.CASCADE)
    block = models.ForeignKey(FocusBlock, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        db_table = 'focus_block_paths'


class FocusSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    focus_length = models.IntegerField(default=25)
    start_time = models.TimeField(blank=True, null=True, default=None)
    focused_on = models.CharField(max_length=100, blank=True, null=True)
    block = models.ForeignKey(FocusBlock, on_delete=models.CASCADE, blank=True, null=True)
    path = models.ForeignKey(FocusPath, on_delete=models.CASCADE, blank=True, null=True)
    minutes_focused = models.IntegerField(default=0)
    entry_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.minutes_focused >= self.user.mins_for_streak:
            self.user.focus_streak += 1
            self.user.focus_streak.save()

        if self.flow:
            self.focus_length = self.flow.total_time

        if self.path:
            self.focus_length = self.path.total_time
        super().save(*args, **kwargs)

    def __str__(self):
        return self.focused_on

    class Meta:
        db_table = 'focus_sessions'


class FocusStat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_time = models.IntegerField(default=0)
    total_focus_sessions = models.IntegerField(default=0)
    focus_session = models.ForeignKey(FocusSession, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'focus_stats'
