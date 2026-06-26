# analyzerapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import Resume, Interview, UserFeedback
from .forms import ResumeUploadForm
from .ai.resume_parser import parse_resume, extract_text_from_resume
from .ai.question_generator import generate_questions
from .ai.scoring_model import calculate_score
from .ai.resume_evaluator import evaluate_resume, get_role_requirements
from django.contrib.sessions.backends.db import SessionStore
  
# ---------- INDEX ----------
ROLE_CHOICES = [
    'Frontend Developer',
    'Backend Developer',
    'Software Developer',
    'Full Stack Developer',
    'UI/UX Designer',
    'Data Analyst',
    'Machine Learning Engineer',
]

TECH_ROLE_KEYWORDS = {
    'Frontend Developer': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'frontend', 'ui', 'web'],
    'Backend Developer': ['python', 'java', 'django', 'flask', 'node', 'api', 'sql', 'database', 'backend'],
    'Software Developer': ['python', 'java', 'c++', 'software', 'programming', 'developer', 'algorithm', 'sql'],
    'Full Stack Developer': ['html', 'css', 'javascript', 'python', 'java', 'react', 'node', 'django', 'sql'],
    'UI/UX Designer': ['ui', 'ux', 'figma', 'wireframe', 'prototype', 'user research', 'interface', 'design'],
    'Data Analyst': ['excel', 'sql', 'python', 'power bi', 'tableau', 'data', 'analytics', 'statistics'],
    'Machine Learning Engineer': ['machine learning', 'deep learning', 'python', 'model', 'tensorflow', 'pytorch', 'nlp', 'ai'],
}
NON_IT_KEYWORDS = [
    'doctor', 'mbbs', 'bds', 'nurse', 'patient', 'hospital', 'clinic', 'medical', 'medicine',
    'surgery', 'pharma', 'pharmacy', 'dentist', 'physician', 'clinical', 'diagnosis',
    'teacher', 'civil engineer', 'mechanical', 'accountant', 'lawyer', 'advocate'
]
GENERAL_TECH_KEYWORDS = sorted({keyword for values in TECH_ROLE_KEYWORDS.values() for keyword in values})

def is_resume_compatible_with_role(resume_text, role):
    text = (resume_text or '').lower()
    if not text.strip():
        return False, 'We could not read enough resume text. Please upload a clear PDF or DOCX resume.'
    role_keywords = TECH_ROLE_KEYWORDS.get(role, [])
    role_hits = sum(1 for keyword in role_keywords if keyword in text)
    tech_hits = sum(1 for keyword in GENERAL_TECH_KEYWORDS if keyword in text)
    non_it_hits = sum(1 for keyword in NON_IT_KEYWORDS if keyword in text)
    if non_it_hits >= 2 and tech_hits < 2:
        return False, f'This resume looks unrelated to {role}. Please upload an IT/software resume or select a role matching your resume.'
    if role_hits == 0 and tech_hits < 2:
        return False, f'This resume does not show enough skills for {role}. Please upload a matching resume before starting the interview.'
    return True, ''

def index(request):
    return render(request, 'index.html')
def pricing(request):
    return render(request, 'pricing.html')


def privacy_policy(request):
    sections = [
        {'heading': 'Information We Collect', 'items': ['Account details such as name, email address, phone number, state, and address.', 'Resume files uploaded by users for analysis and interview preparation.', 'Interview recordings, audio transcripts, answers, ratings, and feedback submitted during the interview flow.']},
        {'heading': 'Camera And Microphone Access', 'items': ['Camera and microphone access is requested only during interview sessions.', 'The access is used to record interview responses and prepare transcripts for review.', 'Users can deny browser permissions, but the interview recording feature may not work without them.']},
        {'heading': 'How We Use Data', 'items': ['To generate resume-based interview questions and performance insights.', 'To show candidate progress, scores, and analytics inside the dashboard.', 'To allow admins to review interview submissions and publish results.']},
        {'heading': 'Storage And Security', 'items': ['Uploaded resumes, interview files, and transcripts are stored in the application storage/database.', 'Access to candidate videos and review controls is restricted to admin users.', 'We do not sell personal data to third parties.']},
    ]
    return render(request, 'legal_page.html', {'title': 'Privacy Policy', 'intro': 'This policy explains how Resume Analyzer AI handles user data, resumes, interview recordings, and analytics.', 'sections': sections})


def terms_and_conditions(request):
    sections = [
        {'heading': 'Use Of The Platform', 'items': ['Users must provide accurate registration and resume information.', 'Users are responsible for the content they upload and submit during interviews.', 'The platform may restrict access if misuse, abuse, or unauthorized activity is detected.']},
        {'heading': 'AI Feedback Disclaimer', 'items': ['AI-generated questions, transcripts, scores, and feedback are preparation aids only.', 'Final hiring or academic decisions should not rely only on automated AI feedback.', 'Admins may review and adjust results before they are shown to users.']},
        {'heading': 'User Responsibilities', 'items': ['Do not upload harmful, illegal, or unrelated files.', 'Do not impersonate another person or submit misleading information.', 'Keep login details private and report unauthorized access immediately.']},
        {'heading': 'Service Changes', 'items': ['Features, pricing, interview limits, and analytics may be updated as the platform improves.', 'We may temporarily suspend features for maintenance or security reasons.']},
    ]
    return render(request, 'legal_page.html', {'title': 'Terms And Conditions', 'intro': 'These terms describe the rules for using Resume Analyzer AI and its interview preparation services.', 'sections': sections})


def refund_policy(request):
    sections = [
        {'heading': 'Subscription Refunds', 'items': ['Refund requests can be reviewed if a paid plan was purchased by mistake or the paid service was not accessible.', 'Refunds are generally not available after substantial use of paid interview or analytics features.', 'Approved refunds will be processed to the original payment method through the payment provider.']},
        {'heading': 'How To Request A Refund', 'items': ['Contact support with your registered email, payment reference, plan name, and reason for the request.', 'Requests should be raised within 7 days of payment for review.', 'The final decision depends on usage history and payment status.']},
        {'heading': 'Test Mode Payments', 'items': ['During development or demo mode, payments may use Razorpay test mode and no real money is charged.', 'Live refunds apply only after Razorpay live mode is enabled and real payments are accepted.']},
    ]
    return render(request, 'legal_page.html', {'title': 'Refund Policy', 'intro': 'This policy explains when refunds may be available for Resume Analyzer AI paid plans.', 'sections': sections})


def contact_us(request):
    sections = [
        {'heading': 'Support', 'items': ['Email: support@resumeanalyzerai.com', 'Phone: Optional - add your business phone number after approval.', 'Business hours: Monday to Friday, 10:00 AM to 6:00 PM IST.']},
        {'heading': 'What To Include', 'items': ['Your registered email address.', 'A short description of the issue.', 'Payment reference or interview submission details if the request is about billing or review.']},
    ]
    return render(request, 'legal_page.html', {'title': 'Contact Us', 'intro': 'Reach out for support, payment queries, interview issues, or account help.', 'sections': sections})

# ---------- USER ----------
def user_register(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if Candidate.objects.filter(email=email).exists():
                return render(request, 'register.html', {'form': form, 'error': 'Email already exists.'})
            
            form.save()
            return redirect('user_login')  # redirect to login page
    else:
        form = CandidateForm()
    return render(request, 'register.html', {'form': form})


from .forms import LoginForm

def user_login(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                candidate = Candidate.objects.get(email=email, password=password)
                request.session['candidate_id'] = candidate.id
                return redirect('user_dashboard')  # make sure this URL exists
            except Candidate.DoesNotExist:
                error = "Invalid email or password."
    else:
        form = LoginForm()

    return render(request, 'user_login.html', {'form': form, 'error': error})


def get_or_create_candidate_for_user(user):
    name = user.get_full_name() or user.username or ''

    if not user.email and name:
        candidate = (
            Candidate.objects
            .filter(name__iexact=name, resumes__isnull=False)
            .distinct()
            .order_by('-submitted_at')
            .first()
        )
        if candidate:
            return candidate

        candidate = Candidate.objects.filter(name__iexact=name).order_by('-submitted_at').first()
        if candidate:
            return candidate

    email = user.email or f"{user.username or user.id}@social.local"
    if not name:
        name = email.split('@')[0]

    candidate, created = Candidate.objects.get_or_create(
        email=email,
        defaults={
            'name': name,
            'phone': '',
            'address': '',
            'state': '',
            'password': 'social-login',
        }
    )
    if not candidate.name and name:
        candidate.name = name
        candidate.save(update_fields=['name'])
    return candidate


def set_candidate_session(request, candidate):
    request.session['candidate_id'] = candidate.id
    latest_resume = candidate.resumes.order_by('-uploaded_at').first()
    if latest_resume and latest_resume.resume_file:
        request.session['uploaded_resume_path'] = latest_resume.resume_file.path



def build_resume_evaluation_for_candidate(candidate, resume_path):
    resume_text = extract_text_from_resume(resume_path)
    role = candidate.interview_role or 'Software Developer'
    evaluation = evaluate_resume(role, get_role_requirements(role), resume_text)
    candidate.resume_evaluation = json.dumps(evaluation, indent=2)
    candidate.resume_score = evaluation.get('overall_resume_score', 0)
    candidate.save(update_fields=['resume_evaluation', 'resume_score'])
    return evaluation


def get_candidate_resume_evaluation(candidate):
    if not candidate or not candidate.resume_evaluation:
        return None
    try:
        return json.loads(candidate.resume_evaluation)
    except (TypeError, ValueError):
        return None


def dashboard_context(candidate):
    evaluation = get_candidate_resume_evaluation(candidate)
    if not evaluation and candidate and candidate.resumes.exists():
        latest_resume = candidate.resumes.order_by('-uploaded_at').first()
        if latest_resume and latest_resume.resume_file:
            try:
                evaluation = build_resume_evaluation_for_candidate(candidate, latest_resume.resume_file.path)
            except Exception:
                evaluation = None
    return {
        'candidate': candidate,
        'role_choices': ROLE_CHOICES,
        'razorpay_key_id': os.environ.get('RAZORPAY_KEY_ID', ''),
        'resume_evaluation': evaluation,
    }
def user_dashboard(request):
    candidate_id = request.session.get('candidate_id')
    if candidate_id:
        candidate = Candidate.objects.get(id=candidate_id)
        set_candidate_session(request, candidate)
        return render(request, 'user_dashboard.html', dashboard_context(candidate))

    if request.user.is_authenticated:
        candidate = get_or_create_candidate_for_user(request.user)
        set_candidate_session(request, candidate)
        return render(request, 'user_dashboard.html', dashboard_context(candidate))

    return redirect('user_login')




from django.core.files.storage import FileSystemStorage

def upload_resume(request):
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        return redirect('user_login')

    candidate = Candidate.objects.get(id=candidate_id)

    if candidate.resumes.exists():
        return redirect('user_dashboard')

    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        selected_role = candidate.interview_role or 'Software Developer'

        # Save to media/resumes/uploaded/
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'resumes/uploaded'))
        filename = fs.save(resume_file.name, resume_file)
        file_path = os.path.join('resumes/uploaded', filename)

        # Save to Resume model
        Resume.objects.update_or_create(
            candidate=candidate,
            defaults={'resume_file': file_path}
        )

        # Save absolute path to session for AI parsing
        absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
        request.session['uploaded_resume_path'] = absolute_path
        candidate.interview_role = selected_role
        candidate.interview_duration = 20
        candidate.interview_question_count = 15
        candidate.status = 'Accepted'
        candidate.score = 0
        candidate.save(update_fields=['interview_role', 'interview_duration', 'interview_question_count', 'status', 'score'])
        build_resume_evaluation_for_candidate(candidate, absolute_path)

        return redirect('user_dashboard')

    return render(request, 'resume_upload.html', {'candidate': candidate, 'role_choices': ROLE_CHOICES})


def update_user_role(request):
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        return redirect('user_login')

    candidate = get_object_or_404(Candidate, id=candidate_id)
    if request.method == 'POST' and not candidate.interview_video:
        selected_role = request.POST.get('interview_role')
        if selected_role in ROLE_CHOICES:
            candidate.interview_role = selected_role
            candidate.interview_duration = 20
            candidate.interview_question_count = 15
            candidate.status = 'Accepted'
            candidate.score = 0
            candidate.save(update_fields=['interview_role', 'interview_duration', 'interview_question_count', 'status', 'score'])
            latest_resume = candidate.resumes.order_by('-uploaded_at').first()
            if latest_resume and latest_resume.resume_file:
                build_resume_evaluation_for_candidate(candidate, latest_resume.resume_file.path)
    return redirect('user_dashboard')


from django.conf import settings
import os

# ---------- SOCIAL LOGIN (Google & Facebook) - Direct OAuth bypass ----------
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.facebook.provider import FacebookProvider
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from django.http import HttpResponseRedirect

def google_login_direct(request):
    """Start Google OAuth through allauth so state/session handling is valid."""
    return redirect('/accounts/google/login/?process=login')

def facebook_login_direct(request):
    """Start Facebook OAuth through allauth, using ngrok when opened locally."""
    host = request.get_host().split(':')[0]
    if host in ('localhost', '127.0.0.1') and settings.OAUTH_DOMAIN:
        return redirect(f"{settings.OAUTH_DOMAIN}/accounts/facebook/login/?process=login")
    return redirect('/accounts/facebook/login/?process=login')

# def resume_upload(request):
#     if request.method == 'POST' and request.FILES.get('resume'):
#         resume = request.FILES['resume']

#         # Save file to resumes/uploaded/
#         upload_dir = os.path.join(settings.BASE_DIR, 'resumes', 'uploaded')
#         os.makedirs(upload_dir, exist_ok=True)

#         fs = FileSystemStorage(location=upload_dir)
#         filename = fs.save(resume.name, resume)
#         full_path = os.path.join(upload_dir, filename)

#         # Save full path in session
#         request.session['uploaded_resume_path'] = full_path

#         return redirect('user_dashboard')
#     return render(request, 'resume_upload.html')
from .models import Candidate
from .forms import CandidateForm
def resume_upload(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save()
            request.session['candidate_id'] = candidate.id
            request.session['uploaded_resume_path'] = candidate.resume_file.path
            return redirect('user_dashboard')
    else:
        form = CandidateForm()
    return render(request, 'resume_upload.html', {'form': form})

from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.db import close_old_connections
import json
import threading
import re
import requests
import base64
import time

_WHISPER_MODEL = None

def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        from faster_whisper import WhisperModel
        model_size = os.environ.get('WHISPER_MODEL_SIZE', 'small.en')
        _WHISPER_MODEL = WhisperModel(model_size, device='cpu', compute_type='int8')
    return _WHISPER_MODEL

def transcribe_video_with_whisper(video_path):
    model = get_whisper_model()
    segments, info = model.transcribe(
        video_path,
        beam_size=1,
        vad_filter=False,
        condition_on_previous_text=False,
        temperature=0,
    )
    whisper_segments = []
    for segment in segments:
        text = segment.text.strip()
        no_speech_prob = float(getattr(segment, 'no_speech_prob', 0) or 0)
        avg_logprob = float(getattr(segment, 'avg_logprob', 0) or 0)
        compression_ratio = float(getattr(segment, 'compression_ratio', 0) or 0)
        if (
            text
            and no_speech_prob <= 0.8
            and avg_logprob >= -1.35
            and compression_ratio <= 3.2
            and not is_probably_hallucinated_answer(text)
        ):
            whisper_segments.append({
                'start': float(segment.start),
                'end': float(segment.end),
                'text': text,
            })
    return whisper_segments

def transcribe_video_with_openai(video_path):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return [], '', 'openai unavailable'

    model_name = os.environ.get('OPENAI_TRANSCRIBE_MODEL', 'whisper-1')
    with open(video_path, 'rb') as audio_file:
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers={'Authorization': f'Bearer {api_key}'},
            data={
                'model': model_name,
                'response_format': 'verbose_json',
                'language': 'en',
            },
            files={'file': (os.path.basename(video_path), audio_file, 'video/webm')},
            timeout=240,
        )
    response.raise_for_status()
    payload = response.json()
    raw_text = (payload.get('text') or '').strip()
    segments = []
    for segment in payload.get('segments') or []:
        text = (segment.get('text') or '').strip()
        if text and not is_probably_hallucinated_answer(text):
            segments.append({
                'start': float(segment.get('start') or 0),
                'end': float(segment.get('end') or 0),
                'text': text,
            })
    return segments, raw_text, f'openai {model_name}'

def transcribe_audio_with_google(audio_path):
    api_key = os.environ.get('GOOGLE_SPEECH_API_KEY')
    if not api_key:
        return [], '', 'google unavailable'

    with open(audio_path, 'rb') as audio_file:
        content = base64.b64encode(audio_file.read()).decode('ascii')

    config = {
        'encoding': 'WEBM_OPUS',
        'sampleRateHertz': 48000,
        'languageCode': os.environ.get('GOOGLE_SPEECH_LANGUAGE', 'en-US'),
        'enableAutomaticPunctuation': True,
        'enableWordTimeOffsets': True,
        'model': os.environ.get('GOOGLE_SPEECH_MODEL', 'latest_long'),
    }
    response = requests.post(
        f'https://speech.googleapis.com/v1/speech:longrunningrecognize?key={api_key}',
        json={'config': config, 'audio': {'content': content}},
        timeout=240,
    )
    response.raise_for_status()
    operation_name = response.json().get('name')
    if not operation_name:
        return [], '', 'google returned no operation'

    operation_url = f'https://speech.googleapis.com/v1/operations/{operation_name}?key={api_key}'
    payload = {}
    for _ in range(60):
        time.sleep(2)
        poll = requests.get(operation_url, timeout=60)
        poll.raise_for_status()
        payload = poll.json()
        if payload.get('done'):
            break

    results = payload.get('response', {}).get('results', [])
    transcript_parts = []
    segments = []
    for result in results:
        alternatives = result.get('alternatives') or []
        if alternatives:
            alternative = alternatives[0]
            text = (alternative.get('transcript') or '').strip()
            if text and not is_probably_hallucinated_answer(text):
                transcript_parts.append(text)
                words = alternative.get('words') or []
                if words:
                    segments.append({
                        'start': google_duration_to_seconds(words[0].get('startTime')),
                        'end': google_duration_to_seconds(words[-1].get('endTime')),
                        'text': text,
                    })

    raw_text = ' '.join(transcript_parts).strip()
    if raw_text and not segments:
        segments.append({'start': 0, 'end': 99999, 'text': raw_text})
    return segments, raw_text, 'google speech-to-text'

def google_duration_to_seconds(value):
    if not value:
        return 0
    value = str(value).strip()
    if value.endswith('s'):
        value = value[:-1]
    try:
        return float(value)
    except ValueError:
        return 0

def transcribe_media_with_best_available_ai(video_path, audio_path=None):
    if audio_path and os.environ.get('GOOGLE_SPEECH_API_KEY'):
        try:
            return transcribe_audio_with_google(audio_path)
        except Exception as error:
            local_segments = transcribe_video_with_whisper(video_path)
            return local_segments, ' '.join(segment['text'] for segment in local_segments), f'local whisper fallback after Google error ({error})'

    if os.environ.get('OPENAI_API_KEY'):
        try:
            return transcribe_video_with_openai(video_path)
        except Exception as error:
            local_segments = transcribe_video_with_whisper(video_path)
            return local_segments, ' '.join(segment['text'] for segment in local_segments), f'local whisper fallback after OpenAI error ({error})'

    local_segments = transcribe_video_with_whisper(video_path)
    return local_segments, ' '.join(segment['text'] for segment in local_segments), 'local whisper'

def normalize_answer_text(text):
    return re.sub(r'[^a-z0-9 ]+', ' ', (text or '').lower()).strip()

def is_probably_hallucinated_answer(text):
    normalized = normalize_answer_text(text)
    if not normalized:
        return True

    hallucination_phrases = [
        'we have a little bit of a response',
        'we have a little bit of response',
        'we have a little answer',
        'this is the technical and the results',
        'this is a simple thing',
        'the next is the results',
        'in the case of this',
        'thank you for watching',
        'thanks for watching',
    ]
    if any(phrase in normalized for phrase in hallucination_phrases):
        return True

    words = normalized.split()
    if len(words) >= 8:
        trigrams = [' '.join(words[index:index + 3]) for index in range(len(words) - 2)]
        repeated = len(trigrams) - len(set(trigrams))
        if repeated >= 3:
            return True

    return False

def answer_word_count(text):
    normalized = normalize_answer_text(text)
    if not normalized or normalized == 'no answer detected':
        return 0
    return len(normalized.split())

def parse_browser_transcript(transcript):
    entries = []
    current = None
    for line in transcript.splitlines():
        line = line.strip()
        if line.startswith('Q:'):
            if current:
                entries.append(current)
            current = {'question': line[2:].strip(), 'answer': ''}
        elif line.startswith('A:') and current:
            current['answer'] = line[2:].strip()
    if current:
        entries.append(current)
    return entries

def build_question_transcript(browser_transcript, answer_windows_json, whisper_segments):
    browser_entries = parse_browser_transcript(browser_transcript)
    try:
        answer_windows = json.loads(answer_windows_json or '[]')
    except json.JSONDecodeError:
        answer_windows = []

    if not answer_windows:
        return browser_transcript, 'browser'

    transcript_blocks = []
    for index, window in enumerate(answer_windows):
        question = window.get('question') or (browser_entries[index]['question'] if index < len(browser_entries) else f'Question {index + 1}')
        start = float(window.get('start') or 0)
        end = float(window.get('end') or start)
        browser_answer = window.get('browserAnswer') or (browser_entries[index]['answer'] if index < len(browser_entries) else '')
        next_start = None
        if index + 1 < len(answer_windows):
            try:
                next_start = float(answer_windows[index + 1].get('start') or 0)
            except (TypeError, ValueError):
                next_start = None

        matched = []
        previous_start = 0
        if index > 0:
            try:
                previous_start = float(answer_windows[index - 1].get('start') or 0)
            except (TypeError, ValueError):
                previous_start = 0
        window_start = ((previous_start + start) / 2) if index > 0 and previous_start < start else max(0, start - 0.25)
        window_end = end + 0.25
        if next_start and next_start > start:
            window_end = (start + next_start) / 2

        for segment_index, segment in enumerate(whisper_segments):
            midpoint = (segment['start'] + segment['end']) / 2
            if window_start <= midpoint < window_end:
                matched.append(segment['text'])
        whisper_answer = ' '.join(matched).strip()
        browser_is_valid = browser_answer and not is_probably_hallucinated_answer(browser_answer)
        if browser_is_valid and answer_word_count(browser_answer) >= answer_word_count(whisper_answer):
            answer = browser_answer
        else:
            answer = whisper_answer
        if not answer and browser_is_valid:
            answer = browser_answer
        answer = strip_question_lead_from_answer(question, answer) or 'No answer detected'
        transcript_blocks.append(f"Q: {question}\nA: {answer}")

    return '\n\n'.join(transcript_blocks), 'whisper'


def strip_question_lead_from_answer(question, answer):
    answer = (answer or '').strip()
    if not answer:
        return answer
    normalized_question = re.sub(r'[^a-z0-9 ]+', ' ', (question or '').lower()).split()
    if normalized_question:
        answer_words = re.sub(r'[^a-z0-9 ]+', ' ', answer.lower()).split()
        if answer_words[:len(normalized_question)] == normalized_question:
            return ' '.join(answer.split()[len(normalized_question):]).strip(' .:-') or 'No answer detected'
        question_phrase = ' '.join(normalized_question)
        normalized_answer = re.sub(r'[^a-z0-9 ]+', ' ', answer.lower()).strip()
        if normalized_answer.startswith(question_phrase[:40]) and '?' in answer[:220]:
            return re.sub(r'^.*?\?\s*', '', answer, count=1).strip() or 'No answer detected'
    if re.match(r'^(how|what|why|when|where|who|explain|tell)\b', answer, re.I) and '?' in answer[:180]:
        return re.sub(r'^.*?\?\s*', '', answer, count=1).strip() or 'No answer detected'
    return answer
def score_transcript(transcript):
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    questions = [line for line in lines if line.startswith('Q:')]
    answers = [line[2:].strip() for line in lines if line.startswith('A:')]
    total_questions = max(len(questions), len(answers), 1)

    useful_answers = []
    unanswered_count = 0
    total_answer_words = 0
    for answer in answers:
        normalized = answer.lower().strip()
        words = [word for word in answer.replace('.', ' ').replace(',', ' ').split() if word.strip()]
        if not answer or normalized == 'no answer detected' or is_probably_hallucinated_answer(answer):
            unanswered_count += 1
            continue
        total_answer_words += len(words)
        if len(words) >= 5:
            useful_answers.append(answer)

    answered_count = len(useful_answers)
    coverage_score = (answered_count / total_questions) * 60
    detail_score = min(total_answer_words / (total_questions * 25), 1) * 30
    completion_score = max(0, ((total_questions - unanswered_count) / total_questions) * 10)
    score = round(coverage_score + detail_score + completion_score)
    score = max(0, min(100, score))

    result = (
        f"AI Result Score: {score}/100\n\n"
        f"Questions asked: {total_questions}\n"
        f"Useful answers: {answered_count}\n"
        f"Unanswered questions: {unanswered_count}\n"
        f"Answer word count: {total_answer_words}\n"
        "Evaluation: "
        + ("Strong answer coverage with enough detail." if score >= 75 else "Needs more complete and detailed answers. Short or missing answers were penalized.")
    )
    return score, result

def process_candidate_transcript(candidate_id, browser_transcript, answer_windows_json, audio_path=None):
    close_old_connections()
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        transcript = browser_transcript
        transcript_source = 'browser'
        raw_transcript_text = ''
        try:
            whisper_segments, raw_transcript_text, ai_source = transcribe_media_with_best_available_ai(candidate.interview_video.path, audio_path)
            transcript, mapping_source = build_question_transcript(browser_transcript, answer_windows_json, whisper_segments)
            transcript_source = f'{ai_source}; mapped with {mapping_source}'
        except Exception as error:
            whisper_segments = []
            transcript_source = f'browser fallback ({error})'

        score, ai_result = score_transcript(transcript)
        raw_transcript_text = raw_transcript_text or ' '.join(segment['text'] for segment in whisper_segments).strip()
        if raw_transcript_text:
            ai_result = f"{ai_result}\n\nFull AI Transcript:\n{raw_transcript_text}"
            transcript = f"{transcript}\n\nFull Continuous Transcript\n==========================\n{raw_transcript_text}"
        candidate.interview_transcript = transcript
        candidate.score = score
        candidate.ai_result = f"{ai_result}\nTranscript source: {transcript_source}"
        candidate.status = 'Pending'
        candidate.save(update_fields=['interview_transcript', 'score', 'ai_result', 'status'])
    finally:
        close_old_connections()

@csrf_exempt
def upload_video(request):
    candidate_id = request.session.get('candidate_id')
    if candidate_id and request.method == 'POST':
        candidate = Candidate.objects.get(id=candidate_id)
        video_data = request.FILES['video']
        candidate.interview_video.save(f"interview_{candidate_id}.webm", video_data)
        audio_path = None
        if 'audio' in request.FILES:
            audio_dir = os.path.join(settings.MEDIA_ROOT, 'interviews')
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, f'interview_{candidate_id}_audio.webm')
            with open(audio_path, 'wb') as audio_file:
                for chunk in request.FILES['audio'].chunks():
                    audio_file.write(chunk)
        browser_transcript = request.POST.get('transcript', '').strip()
        answer_windows_json = request.POST.get('answer_windows', '')
        candidate.interview_transcript = (
            "AI transcript is still processing.\n"
            "Please refresh the admin page and download this DOC again after a few moments."
        )
        candidate.ai_result = 'AI transcript processing started. Admin review required before publishing the result.'
        candidate.status = 'Pending'
        candidate.save(update_fields=['interview_video', 'interview_transcript', 'ai_result', 'status'])

        threading.Thread(
            target=process_candidate_transcript,
            args=(candidate.id, browser_transcript, answer_windows_json, audio_path),
            daemon=True,
        ).start()
        return HttpResponse("Interview uploaded. Transcript processing has started.")
    return HttpResponse("Failed", status=400)


def download_transcript_doc(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    transcript = candidate.interview_transcript or 'No transcript available.'
    if 'Full Continuous Transcript' in transcript:
        question_transcript, full_transcript = transcript.split('Full Continuous Transcript', 1)
        transcript = (
            "Full Continuous Transcript\n"
            f"{full_transcript.strip()}\n\n"
            "Question-wise Transcript\n"
            "========================\n"
            f"{question_transcript.strip()}"
        )
    content = (
        f"Candidate: {candidate.name}\n"
        f"Email: {candidate.email}\n"
        f"Role: {candidate.interview_role}\n"
        f"Score: {candidate.score}/100\n"
        f"Status: {candidate.status}\n\n"
        f"{candidate.ai_result}\n\n"
        "Interview Transcript\n"
        "====================\n"
        f"{transcript}\n"
    )
    response = HttpResponse(content, content_type='application/msword')
    response['Content-Disposition'] = f'attachment; filename="candidate_{candidate.id}_answers.doc"'
    return response


def interview_feedback(request):
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        return redirect('user_login')

    candidate = Candidate.objects.filter(id=candidate_id).first()
    if request.method == 'POST':
        ai_rating = int(request.POST.get('ai_rating') or 3)
        platform_rating = int(request.POST.get('platform_rating') or 3)
        details = request.POST.get('details', '').strip()
        if candidate:
            UserFeedback.objects.create(
                candidate=candidate,
                ai_rating=max(1, min(5, ai_rating)),
                platform_rating=max(1, min(5, platform_rating)),
                details=details,
            )
        return redirect('index')

    return render(request, 'interview_feedback.html', {'candidate': candidate})

# analyzerapp/views.py
from django.shortcuts import render
from .ai.resume_parser import parse_resume, extract_text_from_resume
from .ai.question_generator import generate_questions

def start_interview(request):
    candidate = None
    candidate_id = request.session.get('candidate_id')
    if candidate_id:
        candidate = Candidate.objects.filter(id=candidate_id).first()
        if candidate and candidate.interview_video:
            return redirect('user_dashboard')
        if not candidate or not candidate.resumes.exists():
            return redirect('upload_resume')
    else:
        return redirect('user_login')

    resume_path = request.session.get('uploaded_resume_path')
    if (not resume_path or not os.path.exists(resume_path)) and candidate and candidate.resumes.exists():
        latest_resume = candidate.resumes.order_by('-uploaded_at').first()
        if latest_resume and latest_resume.resume_file:
            resume_path = latest_resume.resume_file.path
            request.session['uploaded_resume_path'] = resume_path

    if resume_path and os.path.exists(resume_path):
        resume_text = extract_text_from_resume(resume_path)
        is_compatible, mismatch_message = is_resume_compatible_with_role(resume_text, candidate.interview_role if candidate else '')
        if not is_compatible:
            messages.error(request, mismatch_message)
            return redirect('user_dashboard')
        parsed = parse_resume(resume_path)
        parsed["target_role"] = candidate.interview_role if candidate else ""
        questions = generate_questions(parsed, candidate.interview_role if candidate else None)
        questions_list = [question.strip() for question in questions.split('\n') if question.strip()]
        if candidate:
            questions_list = questions_list[:candidate.interview_question_count]
    else:
        questions_list = ["Please upload your resume first."]
    
    return render(request, 'interview.html', {'questions': questions_list, 'candidate': candidate})


def user_analytics(request):
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        return redirect('user_login')

    candidate = Candidate.objects.filter(id=candidate_id).first()
    total_steps = 3
    completed_steps = 0
    if candidate and candidate.resumes.exists():
        completed_steps += 1
    if candidate and candidate.interview_video:
        completed_steps += 1
    if candidate and candidate.status != 'Pending':
        completed_steps += 1

    progress = int((completed_steps / total_steps) * 100)
    return render(request, 'analytics.html', {
        'candidate': candidate,
        'progress': progress,
        'completed_steps': completed_steps,
    })



def upload_interview_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        interview = Interview.objects.get(user=request.user)
        video = request.FILES['video']
        interview.video_file.save(f"{request.user.username}_interview.webm", ContentFile(video.read()))
        interview.save()
        return redirect('user_dashboard')
    return render(request, 'interview.html', {'error': 'No video received'})

# ---------- ADMIN ----------
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == 'admin' and password == 'admin':
            request.session['admin_logged_in'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('admin_login')
    return render(request, 'admin_login.html')  

import csv
from django.core.paginator import Paginator
from django.db.models import Q

def admin_dashboard(request, section='dashboard'):
    all_candidates = Candidate.objects.all()
    candidates = all_candidates.order_by('-submitted_at')
    all_feedbacks = UserFeedback.objects.select_related('candidate').order_by('-created_at')

    search = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    role_filter = request.GET.get('role', '').strip()
    sort = request.GET.get('sort', 'newest')

    if search:
        candidates = candidates.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(interview_role__icontains=search)
        )
    if status_filter:
        candidates = candidates.filter(status=status_filter)
    if role_filter:
        candidates = candidates.filter(interview_role=role_filter)

    if sort == 'oldest':
        candidates = candidates.order_by('submitted_at')
    elif sort == 'score':
        candidates = candidates.order_by('-score', '-submitted_at')

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="candidates.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Role', 'Duration', 'Questions', 'Status', 'Score'])
        for candidate in candidates:
            writer.writerow([
                candidate.name,
                candidate.email,
                candidate.interview_role,
                candidate.interview_duration,
                candidate.interview_question_count,
                candidate.status,
                candidate.score,
            ])
        return response

    paginator = Paginator(candidates, 5)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('export', None)

    roles = (
        all_candidates
        .exclude(interview_role='')
        .values_list('interview_role', flat=True)
        .distinct()
        .order_by('interview_role')
    )
    total_candidates = all_candidates.count()
    interviews_conducted = all_candidates.exclude(interview_video='').count()
    accepted_count = all_candidates.filter(status='Accepted').count()
    pending_count = all_candidates.filter(status='Pending').count()
    rejected_count = all_candidates.filter(status='Rejected').count()
    status_total = accepted_count + pending_count + rejected_count or 1
    role_counts = []
    for role in roles:
        role_counts.append({'role': role, 'count': all_candidates.filter(interview_role=role).count()})
    role_counts = sorted(role_counts, key=lambda item: item['count'], reverse=True)[:6]
    max_role_count = max([item['count'] for item in role_counts] or [1])

    resume_total = Resume.objects.count()
    pdf_count = Resume.objects.filter(resume_file__iendswith='.pdf').count()
    docx_count = Resume.objects.filter(resume_file__iendswith='.docx').count()
    resume_base = resume_total or 1
    score_distribution = {
        '90-100': all_candidates.filter(score__gte=90).count(),
        '80-90': all_candidates.filter(score__gte=80, score__lt=90).count(),
        '70-80': all_candidates.filter(score__gte=70, score__lt=80).count(),
        '60-70': all_candidates.filter(score__gte=60, score__lt=70).count(),
        'Below 60': all_candidates.filter(score__lt=60).count(),
    }
    max_score_bucket = max(score_distribution.values() or [1]) or 1
    average_scores_by_role = []
    for item in role_counts:
        role_scores = [c.score for c in all_candidates.filter(interview_role=item['role']).exclude(score__isnull=True)]
        avg = round(sum(role_scores) / len(role_scores), 1) if role_scores else 0
        average_scores_by_role.append({'role': item['role'], 'score': avg})
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr']
    interview_trend = []
    for index, month in enumerate(month_labels, start=1):
        interview_trend.append({
            'month': month,
            'count': all_candidates.filter(interview_video__isnull=False, submitted_at__month=index).exclude(interview_video='').count()
        })
    max_trend = max([item['count'] for item in interview_trend] or [1]) or 1

    context = {
        'admin_section': section,
        'page_title': {
            'dashboard': 'Dashboard Overview',
            'candidates': 'Candidates',
            'interviews': 'Interview Reviews',
            'feedback': 'Feedback',
            'analytics': 'Analytics',
            'settings': 'Settings',
            'users': 'Users',
        }.get(section, 'Dashboard Overview'),
        'page_subtitle': {
            'dashboard': 'Monitor interviews, candidates, role setup, and performance.',
            'candidates': 'Manage candidates, selected roles, resumes, and interview setup.',
            'interviews': 'Review submitted interview videos and publish decisions.',
            'feedback': 'Track candidate feedback and review outcomes.',
            'analytics': 'Understand candidate progress, scores, and review status.',
            'settings': 'Manage interview defaults and admin workflow settings.',
            'users': 'View registered candidate accounts.',
        }.get(section, 'Monitor interviews, candidates, role setup, and performance.'),
        'candidates': page_obj,
        'page_obj': page_obj,
        'roles': roles,
        'search': search,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'sort': sort,
        'query_string': query_params.urlencode(),
        'feedbacks': all_feedbacks,
        'total_candidates': total_candidates,
        'interviews_conducted': interviews_conducted,
        'accepted_count': accepted_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'accepted_percent': round((accepted_count / status_total) * 100),
        'pending_percent': round((pending_count / status_total) * 100),
        'rejected_percent': round((rejected_count / status_total) * 100),
        'accepted_plus_pending_percent': round(((accepted_count + pending_count) / status_total) * 100),
        'role_counts': role_counts,
        'max_role_count': max_role_count,
        'average_scores_by_role': average_scores_by_role,
        'score_distribution': score_distribution,
        'max_score_bucket': max_score_bucket,
        'interview_trend': interview_trend,
        'max_trend': max_trend,
        'total_resumes_uploaded': resume_total,
        'pdf_percent': round((pdf_count / resume_base) * 100),
        'docx_percent': round((docx_count / resume_base) * 100),
    }
    scored = all_candidates.exclude(score__isnull=True)
    scores = [candidate.score for candidate in scored if candidate.score is not None]
    context['average_score'] = round(sum(scores) / len(scores), 1) if scores else 0
    return render(request, 'admin_dashboard.html', context)

def admin_candidates(request):
    return admin_dashboard(request, 'candidates')

def admin_interviews(request):
    return admin_dashboard(request, 'interviews')

def admin_feedback(request):
    return admin_dashboard(request, 'feedback')

def admin_analytics(request):
    return admin_dashboard(request, 'analytics')

def admin_settings(request):
    return admin_dashboard(request, 'settings')

def admin_users(request):
    return admin_dashboard(request, 'users')


from django.views.decorators.csrf import csrf_protect

@csrf_protect
def update_status(request, candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        candidate.status = new_status or candidate.status
        if request.POST.get('interview_role'):
            candidate.interview_role = request.POST.get('interview_role')
        if request.POST.get('interview_duration'):
            try:
                candidate.interview_duration = max(1, int(request.POST.get('interview_duration')))
            except (TypeError, ValueError):
                pass
        if request.POST.get('interview_question_count'):
            try:
                candidate.interview_question_count = max(1, int(request.POST.get('interview_question_count')))
            except (TypeError, ValueError):
                pass

        # Admin can publish or correct the AI-suggested result before users see it.
        if 'score' in request.POST:
            try:
                candidate.score = max(0, min(100, float(request.POST.get('score') or 0)))
            except (TypeError, ValueError):
                pass
        if 'ai_result' in request.POST:
            candidate.ai_result = request.POST.get('ai_result', '').strip()
        candidate.save()
    return redirect('admin_dashboard')

@csrf_protect
def delete_candidate(request, candidate_id):
    if request.method == 'POST':
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.delete()
    return redirect('admin_dashboard')

def score_interview(request, id):
    interview = get_object_or_404(Interview, id=id)
    if request.method == 'POST':
        comm = int(request.POST.get('comm_score'))
        rel = int(request.POST.get('rel_score'))
        conf = int(request.POST.get('conf_score'))
        total = calculate_score(comm, rel, conf)
        interview.communication_score = comm
        interview.relevance_score = rel
        interview.confidence_score = conf
        interview.total_score = total
        interview.save()
        return redirect('admin_dashboard')
    return render(request, 'score_result.html', {'interview': interview})

def accept_interview(request, id):
    interview = get_object_or_404(Interview, id=id)
    interview.status = 'Accepted'
    interview.save()
    return redirect('admin_dashboard')

def reject_interview(request, id):
    interview = get_object_or_404(Interview, id=id)
    interview.status = 'Rejected'
    interview.save()
    return redirect('admin_dashboard')

def admin_logout(request):
    request.session.flush()
    return redirect('index')


from django.contrib.auth import logout
def user_logout(request):
    logout(request)
    return redirect('index')  











