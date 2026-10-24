from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

# Course list view
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-total_enrollment')[:10]

# Course details view
class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'

# Registration view
def registration_request(request):
    context = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['form'] = form
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    else:
        form = UserCreationForm()
        context['form'] = form
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

# Login view
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['error'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)

# Logout view
def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')

# Enroll view
def enroll(request, course_id):
    if request.method == 'POST' and request.user.is_authenticated:
        course = get_object_or_404(Course, pk=course_id)
        # Increase course enrollment count
        course.total_enrollment += 1
        course.save()
        # Create enrollment
        Enrollment.objects.get_or_create(user=request.user, course=course)
        return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))
    return redirect('onlinecourse:index')

# Task 5: Submit exam view
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if not user.is_authenticated:
        return redirect('onlinecourse:login')

    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)

    if request.method == 'POST':
        submission = Submission.objects.create(enrollment=enrollment)

        selected_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_ids.append(int(value))

        submission.choices.set(selected_ids)
        submission.save()

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

    return redirect('onlinecourse:course_details', course_id=course.id)

# Task 5: Show exam result view
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    submitted_choices = submission.choices.all()
    selected_ids = [choice.id for choice in submitted_choices]

    total_score = 0
    questions = course.question_set.all()

    for question in questions:
        total_score += question.grade

    grade = 0
    for question in questions:
        if question.is_get_score(selected_ids):
            grade += question.grade

    context['course'] = course
    context['grade'] = grade
    context['total_score'] = total_score
    context['submission'] = submission

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)