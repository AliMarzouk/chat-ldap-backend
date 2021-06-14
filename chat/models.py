from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from hashlib import sha256

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    highlighted = models.TextField()

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)


class User(AbstractUser):
    login = models.CharField(max_length=100, blank=False, unique=True)
    password = models.CharField(max_length=400, blank=False)
    nom = models.CharField(max_length=100, blank=False)
    prenom = models.CharField(max_length=100, blank=False)
    num = models.IntegerField()
    certification = models.CharField(max_length=400, blank=True, default='')
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'login'

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        hashed = sha256(self.password.encode('utf-8')).hexdigest()
        self.password = hashed
        super(User, self).save(*args, **kwargs)


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_10_messages(user):
        return Message.objects.order_by('-timestamp').filter(Q(author=user) | Q(recipient=user)).all()[:10]

#
#
# class Client(models.Model):
#     def __init__(self, num=0, nom='', prenom='', login='', password='', certification=None):
#         super(Client, self).__init__()
#         self.num = int(num.__str__())
#         self.nom = nom.__str__()
#         self.prenom = prenom.__str__()
#         self.login = login.__str__()
#         self.password = password
#         self.certification = certification
