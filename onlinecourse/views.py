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