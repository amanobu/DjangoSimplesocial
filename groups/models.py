from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
# from accounts.models import User
#markdown形式のデータのパーサっぽい。相互変換
import misaka

from django.contrib.auth import get_user_model
#TODO:これは何だ？
User = get_user_model()

# https://docs.djangoproject.com/en/1.11/howto/custom-template-tags/#inclusion-tags
# This is for the in_group_members check template tag
from django import template

#TODO:これはなんだ？
register = template.Library()



class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    #slug は新聞の用語です。 スラグは、文字、数字、アンダースコア、
    #またはハイフンのみを含む短いラベルです。 一般的に URL 内で使用されます。
    #The 46 Year Old VirginをThe%2046%20Year%20Old%20Virginではなく、the-46-year-old-virginと変換
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField(blank=True, default='')
    description_html = models.TextField(editable=False, default='', blank=True)
    #多対多対応.通常はDjangoが多対多関係を管理する中間テーブルを作成するが
    #throughはそのDjangoの自動的に作る中間テーブルは使用せずに指定する事の様だ
    members = models.ManyToManyField(User,through="GroupMember")

    def __str__(self):
        return self.name

    #saveメソッドをオーバーライドし、slugやdescription_htmlに保存する
    #前に前加工を施す為だと思う
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        self.description_html = misaka.html(self.description)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("groups:single", kwargs={"slug": self.slug})

    class Meta:
        #グループ名でデフォルトソートするのだと思う
        ordering = ["name"]


class GroupMember(models.Model):
    group = models.ForeignKey(Group, related_name="memberships")
    user = models.ForeignKey(User,related_name='user_groups')

    def __str__(self):
        return self.user.username

    class Meta:
        #複合キー
        unique_together = ("group", "user")
