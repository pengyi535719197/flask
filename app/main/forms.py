from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from flask_pagedown.fields import PageDownField
from ..models import User, Role

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('名字', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    name = StringField('名字', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')
    email = StringField('邮箱', validaators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                                                                    0, '用户名必须只有字母数据点或下划线')])
    confirmed = BooleanField('认证')
    role = SelectField('位置', validators=[Length(0, 64)])
    submit = SubmitField('提交')
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm(), self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user =user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')

    def validate_username(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('用户名已经被使用')

class PostForm(FlaskForm):
    body = PageDownField('在此写文章', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = StringField('输入你的评论', validators=[DataRequired()])
    submit = SubmitField('Submit')
