from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# QuestionInline class
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

# ChoiceInline class
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2

# QuestionAdmin class
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text']

# LessonAdmin class
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

# CourseAdmin class
class CourseAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

# Register models
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)