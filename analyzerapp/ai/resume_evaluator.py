import re

ROLE_REQUIREMENTS = {
    'Frontend Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Responsive Design', 'Accessibility', 'Git'],
    'Backend Developer': ['Python', 'Java', 'Django', 'REST API', 'SQL', 'Database Design', 'Authentication', 'Git'],
    'Software Developer': ['Programming', 'Data Structures', 'Algorithms', 'OOP', 'SQL', 'Git', 'Testing'],
    'Full Stack Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Python', 'Django', 'REST API', 'SQL', 'Git'],
    'UI/UX Designer': ['UI Design', 'UX Research', 'Wireframes', 'Prototyping', 'Figma', 'Accessibility', 'User Testing'],
    'Data Analyst': ['Excel', 'SQL', 'Python', 'Power BI', 'Tableau', 'Statistics', 'Data Cleaning', 'Visualization'],
    'Machine Learning Engineer': ['Python', 'Machine Learning', 'Deep Learning', 'NLP', 'TensorFlow', 'PyTorch', 'Model Evaluation', 'Data Processing'],
}

TECHNICAL_CATEGORIES = {
    'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'sql'],
    'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'node', 'express'],
    'libraries': ['pandas', 'numpy', 'scikit', 'tensorflow', 'pytorch', 'matplotlib'],
    'databases': ['mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'sql'],
    'operating_systems': ['linux', 'windows', 'ubuntu'],
    'networking': ['http', 'tcp', 'ip', 'dns', 'network'],
    'cloud': ['aws', 'azure', 'gcp', 'cloud'],
    'ai_ml': ['machine learning', 'deep learning', 'nlp', 'ai'],
    'cybersecurity': ['security', 'authentication', 'authorization', 'encryption'],
    'devops': ['docker', 'kubernetes', 'ci/cd', 'jenkins', 'git', 'github'],
    'api_development': ['api', 'rest', 'graphql', 'json'],
    'architecture_knowledge': ['system design', 'microservices', 'architecture', 'scalable'],
}

SECTION_WORDS = {
    'summary': ['summary', 'objective', 'profile'],
    'skills': ['skills', 'technical skills'],
    'projects': ['projects', 'project'],
    'experience': ['experience', 'internship', 'work'],
    'education': ['education', 'degree', 'university', 'college'],
    'certifications': ['certification', 'certificate'],
}

ACTION_VERBS = ['built', 'developed', 'designed', 'implemented', 'created', 'improved', 'optimized', 'led', 'managed']


def get_role_requirements(role):
    return ROLE_REQUIREMENTS.get(role, ROLE_REQUIREMENTS['Software Developer'])


def _contains_any(text, keywords):
    return [keyword for keyword in keywords if keyword.lower() in text]


def _score_from_ratio(found, total, base=35, span=65):
    if total <= 0:
        return base
    return max(0, min(100, round(base + (len(found) / total) * span)))


def _extract_projects(text):
    projects = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines):
        lower = line.lower()
        if 'project' in lower or any(word in lower for word in ['resume analyzer', 'portfolio', 'management system', 'prediction', 'dashboard']):
            snippet = ' '.join(lines[index:index + 3])[:420]
            projects.append({'name': line[:80], 'description': snippet})
    return projects[:5]


def evaluate_resume(selected_role, role_requirements, resume_text):
    text = (resume_text or '').strip()
    lower = text.lower()
    words = re.findall(r'[a-zA-Z+#.]+', lower)
    word_count = len(words)

    role_requirements = role_requirements or get_role_requirements(selected_role)
    matching_skills = sorted(set(_contains_any(lower, role_requirements)))
    all_role_skills = [skill for skill in role_requirements]
    missing_skills = [skill for skill in all_role_skills if skill.lower() not in lower]

    section_hits = {name: any(word in lower for word in markers) for name, markers in SECTION_WORDS.items()}
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text))
    has_phone = bool(re.search(r'(\+91)?[6-9]\d{9}', text))
    has_numbers = bool(re.search(r'\d+%|\d+\+|\b\d{2,}\b', text))
    action_hits = _contains_any(lower, ACTION_VERBS)

    ats_issues = []
    if not has_email:
        ats_issues.append('Email address is missing or not readable.')
    if not has_phone:
        ats_issues.append('Indian phone number is missing or not readable.')
    for section, exists in section_hits.items():
        if not exists and section in ['skills', 'projects', 'education']:
            ats_issues.append(f'{section.title()} section is missing or unclear.')
    if word_count < 180:
        ats_issues.append('Resume content appears too short for a complete evaluation.')
    if len(matching_skills) < max(2, len(role_requirements) // 3):
        ats_issues.append('Role-specific keyword coverage is low.')

    ats_score = 100 - min(55, len(ats_issues) * 9)
    formatting_score = 80 if word_count >= 180 else 58
    if all(section_hits.values()):
        formatting_score += 8
    formatting_score = min(100, formatting_score)

    role_match_score = _score_from_ratio(matching_skills, len(role_requirements), base=25, span=70)

    technical_skill_analysis = {}
    category_scores = []
    for category, keywords in TECHNICAL_CATEGORIES.items():
        found = _contains_any(lower, keywords)
        score = _score_from_ratio(found, len(keywords), base=20, span=75)
        category_scores.append(score)
        technical_skill_analysis[category] = {
            'score': score,
            'found': found,
            'missing': [keyword for keyword in keywords if keyword not in found],
        }
    technical_score = round(sum(category_scores) / len(category_scores)) if category_scores else 0

    projects = _extract_projects(text)
    project_analysis = []
    for project in projects:
        used = _contains_any(project['description'].lower(), [kw for kws in TECHNICAL_CATEGORIES.values() for kw in kws])
        project_score = min(100, 45 + len(used) * 8 + (10 if has_numbers else 0))
        project_analysis.append({
            'project_name': project['name'],
            'business_value': 'Clearer business outcome is needed.' if not has_numbers else 'Shows measurable or concrete outcome.',
            'technical_complexity': 'Moderate' if len(used) >= 3 else 'Basic',
            'innovation_level': 'Moderate' if len(used) >= 4 else 'Needs more uniqueness.',
            'industry_relevance': 'Relevant to selected role.' if matching_skills else 'Role relevance is unclear.',
            'technologies_used': used,
            'recruiter_impression': 'Promising, but impact and technical depth should be clearer.',
            'project_score': project_score,
            'improvement_suggestions': ['Add problem statement, architecture, tools used, and measurable result.'],
            'missing_features': ['Deployment link', 'GitHub link', 'Quantified impact'],
            'recommended_enhancements': ['Add screenshots, live demo, tests, and role-specific technologies.'],
        })

    projects_score = round(sum(p['project_score'] for p in project_analysis) / len(project_analysis)) if project_analysis else 35
    experience_score = 70 if section_hits['experience'] else 38
    if action_hits:
        experience_score += 10
    if has_numbers:
        experience_score += 10
    experience_score = min(100, experience_score)
    education_score = 78 if section_hits['education'] else 45
    certification_score = 75 if section_hits['certifications'] else 35
    resume_quality_score = round((ats_score + formatting_score + role_match_score + projects_score) / 4)
    interview_readiness_score = round((technical_score * 0.45) + (role_match_score * 0.35) + (experience_score * 0.20))
    overall_resume_score = round((ats_score + role_match_score + technical_score + projects_score + experience_score + education_score + certification_score + resume_quality_score + interview_readiness_score) / 9)

    if overall_resume_score >= 85:
        candidate_level = 'Mid-Level'
    elif overall_resume_score >= 70:
        candidate_level = 'Associate'
    elif overall_resume_score >= 55:
        candidate_level = 'Entry-Level'
    else:
        candidate_level = 'Beginner'

    recommended_skills = missing_skills[:8]
    strengths = []
    if matching_skills:
        strengths.append('Resume contains role-relevant keywords: ' + ', '.join(matching_skills[:6]))
    if section_hits['projects']:
        strengths.append('Projects section is present.')
    if section_hits['education']:
        strengths.append('Education section is present.')
    if has_numbers:
        strengths.append('Some quantified details are present.')
    strengths.extend(['Readable resume text was extracted.', 'Candidate has a selected target role.'])
    weaknesses = ats_issues[:]
    if not has_numbers:
        weaknesses.append('Achievements are not quantified enough.')
    if not project_analysis:
        weaknesses.append('Projects are missing or not clearly described.')
    if not section_hits['certifications']:
        weaknesses.append('Relevant certifications are missing.')

    high = missing_skills[:4] + ats_issues[:2]
    medium = ['Add measurable achievements.', 'Improve project descriptions.', 'Add GitHub/portfolio links.']
    low = ['Polish grammar and formatting consistency.', 'Keep resume length focused.']

    return {
        'candidate_level': candidate_level,
        'overall_resume_score': overall_resume_score,
        'ats_score': ats_score,
        'role_match_score': role_match_score,
        'technical_score': technical_score,
        'projects_score': projects_score,
        'experience_score': experience_score,
        'education_score': education_score,
        'certification_score': certification_score,
        'formatting_score': formatting_score,
        'resume_quality_score': resume_quality_score,
        'interview_readiness_score': interview_readiness_score,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'recommended_skills': recommended_skills,
        'outdated_skills': [],
        'technical_skill_analysis': technical_skill_analysis,
        'project_analysis': project_analysis,
        'experience_analysis': {
            'present': section_hits['experience'],
            'impact': 'Good' if has_numbers else 'Needs quantified impact.',
            'action_verbs': action_hits,
            'score': experience_score,
        },
        'education_analysis': {
            'present': section_hits['education'],
            'score': education_score,
            'comment': 'Education is visible.' if section_hits['education'] else 'Education details are missing.'
        },
        'certification_analysis': {
            'present': section_hits['certifications'],
            'score': certification_score,
            'recommended_certifications': ['Role-specific certification', 'Cloud fundamentals', 'Git/GitHub or testing certification']
        },
        'ats_issues': ats_issues,
        'resume_improvements': [
            'Add a strong professional summary aligned with the selected role.',
            'Add role-specific keywords from the job requirements.',
            'Quantify project and experience outcomes wherever possible.',
            'Include GitHub, LinkedIn, and portfolio links if available.',
            'Keep headings simple: Summary, Skills, Projects, Experience, Education, Certifications.'
        ],
        'market_recommendations': [
            'Build two role-specific portfolio projects.',
            'Add deployment links and clean GitHub README files.',
            'Practice technical, behavioral, and role-specific interview topics.',
            'Strengthen missing skills: ' + ', '.join(recommended_skills[:5]) if recommended_skills else 'Continue deepening current role skills.'
        ],
        'interview_topics': recommended_skills[:6] + ['Resume walkthrough', 'Project explanation', 'Behavioral STAR answers'],
        'career_roadmap': [
            'Fix ATS and formatting issues first.',
            'Add missing role skills and projects.',
            'Improve GitHub/LinkedIn/portfolio proof.',
            'Practice interview questions based on weak areas.'
        ],
        'strengths': strengths[:10],
        'weaknesses': weaknesses[:10],
        'improvement_priority': {'high': high[:10], 'medium': medium, 'low': low},
        'hiring_probability': {
            'startup': 'Medium' if overall_resume_score >= 60 else 'Low',
            'service_company': 'Medium' if overall_resume_score >= 55 else 'Low',
            'product_company': 'Medium' if overall_resume_score >= 75 else 'Low',
            'enterprise': 'Medium' if ats_score >= 70 and role_match_score >= 65 else 'Low'
        },
        'final_recruiter_summary': (
            f'This resume is evaluated as {candidate_level} for {selected_role}. '
            f'Overall score is {overall_resume_score}/100. Key strengths include role keyword matches and available sections. '
            f'Primary concerns are: {", ".join(weaknesses[:3]) if weaknesses else "few major concerns"}. '
            f'{"Would shortlist for initial screening." if overall_resume_score >= 70 else "Would not shortlist yet without improvements."}'
        )
    }
