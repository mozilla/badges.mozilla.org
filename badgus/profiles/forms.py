from django import forms
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import UserChangeForm

from django.utils.translation import ugettext_lazy as _

from .models import UserProfile


class MyForm(forms.Form):

    required_css_class = "required"
    error_css_class = "error"

    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row=(u'<li%(html_class_attr)s>%(label)s %(field)s' +
                '%(help_text)s%(errors)s</li>'),
            error_row=u'<li>%s</li>',
            row_ender='</li>',
            help_text_html=u' <p class="help">%s</p>',
            errors_on_separate_row=False)


class MyModelForm(forms.ModelForm):

    required_css_class = "required"
    error_css_class = "error"

    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row=(u'<li%(html_class_attr)s>%(label)s %(field)s' +
                '%(help_text)s%(errors)s</li>'),
            error_row=u'<li>%s</li>',
            row_ender='</li>',
            help_text_html=u' <p class="help">%s</p>',
            errors_on_separate_row=False)


class UserEditForm(MyForm):

    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': 
            _("This value may contain only letters, numbers and @/./+/-/_ characters.")})

    def __init__(self, *args, **kwargs):

        profile = kwargs['profile']
        del kwargs['profile']

        super(UserEditForm, self).__init__(*args, **kwargs)

        remaining = profile.username_changes_remaining()
        self.fields['username'].help_text = (
                _('Changes remaining: %s') % remaining)
        self.initial['username'] = profile.user.username

    def clean_username(self):
        data = self.cleaned_data['username']
        if (data != self.initial['username'] and
                User.objects.filter(username=data).count() > 0):
            err_str = _('New username already taken by another profile')
            raise forms.ValidationError(err_str)
        return data


class UserProfileEditForm(MyModelForm):

    class Meta:
        model = UserProfile
        fields = ('display_name', 'avatar', 'location', 'bio', )

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
