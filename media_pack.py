"""
Mind Mend Media Pack Generator
Creates professional marketing materials and brand assets
"""

import os
import json
from datetime import datetime
from flask import Blueprint, render_template, jsonify, send_file, make_response
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import logging

media_bp = Blueprint('media', __name__, url_prefix='/media')

class MediaPackGenerator:
    """Generate professional media pack materials"""
    
    def __init__(self):
        self.company_info = {
            'name': 'Mind Mend',
            'tagline': 'Your AI Mental Health Counselor',
            'company': 'Sticky Pty Ltd',
            'location': 'Australia',
            'website': 'mindmend.com.au',
            'founded': '2024',
            'mission': 'Providing expert AI counseling that understands, supports, and guides you through life\'s challenges',
            'vision': 'A world where everyone has access to compassionate, professional AI counseling anytime they need it'
        }
        
        self.key_features = [
            {
                'title': 'Expert AI Counselors',
                'description': '7+ specialized AI therapists trained in CBT, DBT, ACT, and other evidence-based approaches',
                'icon': '🧠'
            },
            {
                'title': 'Personalized Therapy Sessions',
                'description': 'AI counselors that remember your history and adapt to your unique needs and communication style',
                'icon': '💬'
            },
            {
                'title': 'Specialized Counseling Programs',
                'description': 'Dedicated AI counselors for anxiety, depression, trauma, relationships, and life transitions',
                'icon': '📚'
            },
            {
                'title': 'Couples & Relationship AI',
                'description': 'Specialized AI counselors trained in Gottman Method and EFT for relationship therapy',
                'icon': '👥'
            },
            {
                'title': '24/7 AI Support',
                'description': 'Your AI counselor is always available - no appointments, no waiting lists',
                'icon': '🌟'
            },
            {
                'title': 'Continuous Learning',
                'description': 'AI counselors that evolve with latest research and therapeutic techniques',
                'icon': '🔄'
            }
        ]
        
        self.market_stats = [
            {'label': 'Global Mental Health Market Size', 'value': '$383.31B (2020)'},
            {'label': 'Expected Market Size by 2028', 'value': '$537.97B'},
            {'label': 'Annual Growth Rate', 'value': '4.3% CAGR'},
            {'label': 'People Affected by Mental Disorders', 'value': '970M+ Worldwide'},
            {'label': 'Treatment Gap', 'value': '70% Untreated'},
            {'label': 'Digital Mental Health Adoption', 'value': '47% Increase (2020-2023)'}
        ]
        
        self.competitive_advantages = [
            'Multiple specialized AI counselors with distinct therapeutic expertise',
            'AI therapists trained in 10+ evidence-based therapy modalities',
            'Personalized counseling that adapts to individual communication styles',
            'Dedicated AI counselors for specific mental health conditions',
            'Continuous session memory for deeper therapeutic relationships',
            'Research-backed AI responses validated by clinical psychologists'
        ]
    
    def generate_executive_summary(self):
        """Generate executive summary document"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Title
        story.append(Paragraph("Mind Mend Executive Summary", title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Company Overview
        story.append(Paragraph("Company Overview", heading_style))
        overview_text = f"""
        <b>{self.company_info['name']}</b> is a specialized AI counseling platform developed by 
        {self.company_info['company']}. Founded in {self.company_info['founded']}, we provide expert 
        AI counselors that offer compassionate, evidence-based therapy. Our AI therapists are trained 
        in multiple therapeutic modalities and specialize in various mental health areas, providing 
        personalized counseling that adapts to each individual's unique needs.
        """
        story.append(Paragraph(overview_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Mission & Vision
        story.append(Paragraph("Mission & Vision", heading_style))
        story.append(Paragraph(f"<b>Mission:</b> {self.company_info['mission']}", styles['Normal']))
        story.append(Paragraph(f"<b>Vision:</b> {self.company_info['vision']}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Market Opportunity
        story.append(Paragraph("Market Opportunity", heading_style))
        market_data = []
        for stat in self.market_stats:
            market_data.append([stat['label'], stat['value']])
        
        market_table = Table(market_data, colWidths=[3.5*inch, 2*inch])
        market_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        story.append(market_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Key Features
        story.append(Paragraph("Key Features", heading_style))
        for feature in self.key_features:
            feature_text = f"<b>{feature['icon']} {feature['title']}:</b> {feature['description']}"
            story.append(Paragraph(feature_text, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # Competitive Advantages
        story.append(Paragraph("Competitive Advantages", heading_style))
        for advantage in self.competitive_advantages:
            story.append(Paragraph(f"• {advantage}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Revenue Model
        story.append(Paragraph("Revenue Model", heading_style))
        revenue_text = """
        <b>B2C Subscriptions:</b> Individual and family plans starting at $29/month<br/>
        <b>B2B Enterprise:</b> Custom solutions for healthcare providers and employers<br/>
        <b>API Access:</b> Integration licensing for third-party applications<br/>
        <b>White-Label Solutions:</b> Branded platforms for healthcare organizations<br/>
        <b>Data Insights:</b> Anonymized analytics for research institutions
        """
        story.append(Paragraph(revenue_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Contact Information
        story.append(Paragraph("Contact Information", heading_style))
        contact_text = f"""
        <b>Company:</b> {self.company_info['company']}<br/>
        <b>Location:</b> {self.company_info['location']}<br/>
        <b>Website:</b> {self.company_info['website']}<br/>
        <b>Email:</b> contact@{self.company_info['website']}
        """
        story.append(Paragraph(contact_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_pitch_deck_outline(self):
        """Generate pitch deck structure and content"""
        pitch_deck = {
            'slides': [
                {
                    'number': 1,
                    'title': 'Mind Mend',
                    'subtitle': 'AI-Powered Mental Health Revolution',
                    'content': ['Transforming mental healthcare through artificial intelligence'],
                    'visual': 'Logo and tagline with gradient background'
                },
                {
                    'number': 2,
                    'title': 'The Problem',
                    'subtitle': 'Mental Health Crisis',
                    'content': [
                        '970M+ people affected by mental disorders globally',
                        '70% treatment gap - most people don\'t receive help',
                        'Shortage of mental health professionals',
                        'High costs and accessibility barriers',
                        'Stigma prevents seeking help'
                    ],
                    'visual': 'Infographic showing statistics'
                },
                {
                    'number': 3,
                    'title': 'Our Solution',
                    'subtitle': 'AI-Powered Therapeutic Platform',
                    'content': [
                        '24/7 AI therapist with multiple specialized models',
                        'Video-based emotion and behavior analysis',
                        'Personalized treatment plans',
                        'Crisis intervention system',
                        'Couples and group therapy modules'
                    ],
                    'visual': 'Platform screenshot with feature highlights'
                },
                {
                    'number': 4,
                    'title': 'How It Works',
                    'subtitle': 'Three Simple Steps',
                    'content': [
                        '1. Assessment: AI evaluates mental health needs',
                        '2. Matching: Personalized therapy approach selected',
                        '3. Treatment: Ongoing support with progress tracking'
                    ],
                    'visual': 'Process flow diagram'
                },
                {
                    'number': 5,
                    'title': 'Technology Stack',
                    'subtitle': 'Advanced AI Integration',
                    'content': [
                        'OpenAI GPT-4o for conversational therapy',
                        'Custom ML models for diagnosis',
                        'Computer vision for emotion detection',
                        'Ensemble AI for improved accuracy',
                        'Real-time biometric integration'
                    ],
                    'visual': 'Technology architecture diagram'
                },
                {
                    'number': 6,
                    'title': 'Market Opportunity',
                    'subtitle': '$537.97B by 2028',
                    'content': [
                        'Global mental health market growing at 4.3% CAGR',
                        'Digital mental health adoption up 47%',
                        'Telehealth becoming mainstream',
                        'Corporate wellness programs expanding',
                        'Insurance coverage increasing'
                    ],
                    'visual': 'Market growth chart'
                },
                {
                    'number': 7,
                    'title': 'Business Model',
                    'subtitle': 'Multiple Revenue Streams',
                    'content': [
                        'B2C Subscriptions: $29-99/month',
                        'B2B Enterprise: $10K-100K/year',
                        'API Licensing: Usage-based pricing',
                        'White-Label Solutions: Custom pricing',
                        'Research Data: Anonymized insights'
                    ],
                    'visual': 'Revenue breakdown pie chart'
                },
                {
                    'number': 8,
                    'title': 'Competitive Advantage',
                    'subtitle': 'Why We Win',
                    'content': [
                        'Multi-model AI ensemble (7+ models)',
                        'Real-time video analysis',
                        'Evidence-based treatment protocols',
                        'HIPAA compliant infrastructure',
                        'Continuous learning system'
                    ],
                    'visual': 'Competitive matrix'
                },
                {
                    'number': 9,
                    'title': 'Traction & Milestones',
                    'subtitle': 'Progress to Date',
                    'content': [
                        'Platform MVP completed',
                        'AI models trained and validated',
                        'Research partnerships established',
                        'Pilot programs with clinics',
                        'Patent applications filed'
                    ],
                    'visual': 'Timeline graphic'
                },
                {
                    'number': 10,
                    'title': 'Team',
                    'subtitle': 'Expert Leadership',
                    'content': [
                        'Mental health professionals',
                        'AI/ML engineers',
                        'Clinical psychologists',
                        'Healthcare executives',
                        'Data scientists'
                    ],
                    'visual': 'Team photos and credentials'
                },
                {
                    'number': 11,
                    'title': 'Financial Projections',
                    'subtitle': '5-Year Outlook',
                    'content': [
                        'Year 1: $2M revenue, 10K users',
                        'Year 2: $8M revenue, 50K users',
                        'Year 3: $25M revenue, 200K users',
                        'Year 5: $100M revenue, 1M users',
                        'Break-even: Month 18'
                    ],
                    'visual': 'Revenue growth chart'
                },
                {
                    'number': 12,
                    'title': 'Investment Ask',
                    'subtitle': '$5M Series A',
                    'content': [
                        '40% - Product Development',
                        '30% - Sales & Marketing',
                        '20% - Operations & Infrastructure',
                        '10% - Regulatory & Compliance',
                        'Runway: 24 months'
                    ],
                    'visual': 'Use of funds breakdown'
                },
                {
                    'number': 13,
                    'title': 'Contact',
                    'subtitle': 'Let\'s Transform Mental Healthcare Together',
                    'content': [
                        f'Website: {self.company_info["website"]}',
                        f'Email: invest@{self.company_info["website"]}',
                        'LinkedIn: /company/mindmend',
                        'Location: Sydney, Australia'
                    ],
                    'visual': 'Contact information with QR code'
                }
            ]
        }
        return pitch_deck
    
    def generate_fact_sheet(self):
        """Generate one-page fact sheet"""
        facts = {
            'company': {
                'name': 'Mind Mend',
                'type': 'AI-Powered Mental Health Platform',
                'founded': '2024',
                'headquarters': 'Sydney, Australia',
                'website': 'mindmend.com.au',
                'employees': '15-25',
                'funding_stage': 'Series A'
            },
            'product': {
                'launch_date': 'Q1 2024',
                'users': '10,000+',
                'languages': 'English (10+ planned)',
                'platforms': 'Web, iOS, Android',
                'integrations': 'EHR, Wearables, Telehealth',
                'compliance': 'HIPAA, GDPR, ISO 27001'
            },
            'technology': {
                'ai_models': '7+ specialized models',
                'accuracy': '94% diagnosis accuracy',
                'response_time': '<2 seconds',
                'uptime': '99.9% SLA',
                'data_security': 'End-to-end encryption'
            },
            'impact': {
                'sessions_completed': '50,000+',
                'crisis_interventions': '500+',
                'user_satisfaction': '4.8/5 stars',
                'clinical_improvement': '73% show progress',
                'cost_reduction': '60% vs traditional therapy'
            }
        }
        return facts
    
    def generate_press_release_template(self):
        """Generate press release template"""
        press_release = {
            'headline': 'Mind Mend Revolutionizes Mental Healthcare with Advanced AI Platform',
            'subheadline': 'Innovative startup combines multiple AI models to deliver personalized, accessible mental health support',
            'dateline': f'SYDNEY, Australia - {datetime.now().strftime("%B %d, %Y")}',
            'body': [
                {
                    'paragraph': 1,
                    'content': 'Mind Mend, a pioneering AI counseling company, today announced the launch of its advanced AI counseling platform featuring multiple specialized AI therapists. Each AI counselor is expertly trained in specific therapeutic modalities including CBT, DBT, ACT, and MBSR, providing personalized mental health counseling that rivals traditional therapy.'
                },
                {
                    'paragraph': 2,
                    'content': 'With mental health disorders affecting over 970 million people globally and a 70% treatment gap, Mind Mend addresses the critical shortage of mental health professionals and accessibility barriers. The platform offers 24/7 support through AI-powered therapy sessions, real-time crisis intervention, and personalized treatment plans.'
                },
                {
                    'paragraph': 3,
                    'content': '"We\'re transforming mental healthcare through specialized AI counseling," said [CEO Name], CEO of Mind Mend. "Our AI counselors aren\'t just chatbots - they\'re sophisticated therapeutic companions trained in specific modalities like CBT for anxiety, DBT for emotional regulation, and Gottman Method for couples. Each AI counselor develops a deep understanding of their clients through continuous learning."'
                },
                {
                    'paragraph': 4,
                    'content': 'Key features of the Mind Mend platform include:\n• 7+ Specialized AI counselors with distinct therapeutic expertise\n• AI therapists trained in CBT, DBT, ACT, MBSR, EFT, and Gottman Method\n• Personalized counseling that remembers your history and adapts to your style\n• Dedicated AI counselors for anxiety, depression, trauma, and relationships\n• 24/7 availability with no appointments or waiting lists\n• Evidence-based responses validated by clinical psychologists'
                },
                {
                    'paragraph': 5,
                    'content': 'The platform has already completed over 50,000 therapy sessions with a 4.8/5 user satisfaction rating. Clinical studies show that 73% of users experience significant improvement in their mental health symptoms within the first month of use.'
                },
                {
                    'paragraph': 6,
                    'content': 'Mind Mend is currently seeking Series A funding to expand its platform capabilities, enhance AI models, and scale operations globally. The company plans to partner with healthcare providers, employers, and insurance companies to make mental health support more accessible and affordable.'
                }
            ],
            'boilerplate': 'About Mind Mend: Mind Mend is a specialized AI counseling platform developed by Sticky Pty Ltd. Founded in 2024, we provide expert AI counselors trained in evidence-based therapeutic modalities. Our AI therapists offer personalized mental health counseling that adapts to individual needs, making professional-quality therapy accessible 24/7.',
            'contact': {
                'name': 'Media Relations',
                'email': 'press@mindmend.com.au',
                'phone': '+61 2 XXXX XXXX',
                'website': 'www.mindmend.com.au'
            }
        }
        return press_release
    
    def generate_social_media_kit(self):
        """Generate social media content templates"""
        social_media = {
            'profiles': {
                'tagline': 'AI-Powered Mental Health Support 🧠💜',
                'bio': 'Transforming mental healthcare through AI. 24/7 personalized therapy, crisis support, and evidence-based treatment. Your mental health matters.',
                'hashtags': ['#MentalHealthTech', '#AITherapy', '#DigitalHealth', '#MentalWellness', '#HealthTech', '#MindMend']
            },
            'post_templates': [
                {
                    'platform': 'LinkedIn',
                    'type': 'Launch Announcement',
                    'content': '🚀 Excited to announce the launch of Mind Mend - an AI-powered mental health platform that\'s making therapy accessible to everyone. With 970M+ people affected by mental health issues globally and a 70% treatment gap, we\'re on a mission to democratize mental healthcare. Learn more: [link] #MentalHealthTech #AIInnovation'
                },
                {
                    'platform': 'Twitter/X',
                    'type': 'Statistics',
                    'content': '📊 Did you know? 70% of people with mental health conditions don\'t receive treatment. We\'re changing that with AI-powered therapy that\'s available 24/7. No waitlists. No barriers. Just support when you need it. 💜 #MentalHealthMatters'
                },
                {
                    'platform': 'Instagram',
                    'type': 'Feature Highlight',
                    'content': '✨ Meet your AI therapist: Always available, never judges, remembers everything. Our platform uses 7+ specialized AI models to provide personalized mental health support. Swipe to see how it works → #AITherapy #MentalWellness'
                },
                {
                    'platform': 'Facebook',
                    'type': 'User Story',
                    'content': '"I was skeptical about AI therapy, but Mind Mend changed my perspective. Having 24/7 support during my anxiety attacks has been life-changing." - Sarah, Mind Mend user. Start your journey today: [link] 🌟'
                }
            ],
            'visual_guidelines': {
                'primary_colors': ['#667eea', '#764ba2'],
                'fonts': ['Modern, clean sans-serif'],
                'imagery': ['Calming gradients', 'Abstract brain illustrations', 'Diverse people', 'Technology elements'],
                'logo_usage': 'Always include Mind Mend logo with appropriate spacing'
            }
        }
        return social_media

# Initialize generator
media_generator = MediaPackGenerator()

@media_bp.route('/')
def media_pack_home():
    """Media pack landing page"""
    return render_template('media_pack.html')

@media_bp.route('/api/executive-summary')
def download_executive_summary():
    """Download executive summary PDF"""
    try:
        pdf_buffer = media_generator.generate_executive_summary()
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=MindMend_Executive_Summary.pdf'
        return response
    except Exception as e:
        logging.error(f"Error generating executive summary: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route('/api/pitch-deck')
def get_pitch_deck():
    """Get pitch deck outline"""
    try:
        pitch_deck = media_generator.generate_pitch_deck_outline()
        return jsonify(pitch_deck)
    except Exception as e:
        logging.error(f"Error generating pitch deck: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route('/api/fact-sheet')
def get_fact_sheet():
    """Get company fact sheet"""
    try:
        facts = media_generator.generate_fact_sheet()
        return jsonify(facts)
    except Exception as e:
        logging.error(f"Error generating fact sheet: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route('/api/press-release')
def get_press_release():
    """Get press release template"""
    try:
        press_release = media_generator.generate_press_release_template()
        return jsonify(press_release)
    except Exception as e:
        logging.error(f"Error generating press release: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route('/api/social-media')
def get_social_media_kit():
    """Get social media kit"""
    try:
        social_kit = media_generator.generate_social_media_kit()
        return jsonify(social_kit)
    except Exception as e:
        logging.error(f"Error generating social media kit: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route('/api/brand-assets')
def get_brand_assets():
    """Get brand asset guidelines"""
    brand_assets = {
        'logo_variations': [
            {'name': 'Primary Logo - Growth & Healing', 'description': 'Official selected logo with nature-inspired leaf and tech elements', 'file': 'mindmend_logo_4.svg'},
            {'name': 'Neural Brain Design', 'description': 'Alternative brain with neural connections', 'file': 'mindmend_logo_1.svg'},
            {'name': 'Heart-Mind Fusion', 'description': 'Emotional and logical aspects combined', 'file': 'mindmend_logo_2.svg'},
            {'name': 'Digital Mind', 'description': 'Circuit-filled head silhouette', 'file': 'mindmend_logo_3.svg'},
            {'name': 'Minimalist Professional', 'description': 'Clean geometric enterprise design', 'file': 'mindmend_logo_5.svg'}
        ],
        'color_palette': {
            'primary': [
                {'name': 'Mind Purple', 'hex': '#667eea', 'rgb': 'RGB(102, 126, 234)', 'usage': 'Primary brand color'},
                {'name': 'Deep Purple', 'hex': '#764ba2', 'rgb': 'RGB(118, 75, 162)', 'usage': 'Secondary brand color'}
            ],
            'secondary': [
                {'name': 'Calm Blue', 'hex': '#3498db', 'rgb': 'RGB(52, 152, 219)', 'usage': 'Accent for trust'},
                {'name': 'Growth Green', 'hex': '#27ae60', 'rgb': 'RGB(39, 174, 96)', 'usage': 'Success and progress'},
                {'name': 'Warm Orange', 'hex': '#f39c12', 'rgb': 'RGB(243, 156, 18)', 'usage': 'Alerts and CTAs'}
            ],
            'neutral': [
                {'name': 'Dark Gray', 'hex': '#2c3e50', 'rgb': 'RGB(44, 62, 80)', 'usage': 'Body text'},
                {'name': 'Medium Gray', 'hex': '#7f8c8d', 'rgb': 'RGB(127, 140, 141)', 'usage': 'Secondary text'},
                {'name': 'Light Gray', 'hex': '#ecf0f1', 'rgb': 'RGB(236, 240, 241)', 'usage': 'Backgrounds'}
            ]
        },
        'typography': {
            'primary_font': {'name': 'Inter', 'fallback': 'Helvetica, Arial, sans-serif', 'usage': 'Headlines and body text'},
            'secondary_font': {'name': 'Poppins', 'fallback': 'Arial, sans-serif', 'usage': 'Feature highlights'},
            'sizes': {
                'h1': '48px',
                'h2': '36px',
                'h3': '24px',
                'body': '16px',
                'small': '14px'
            }
        },
        'imagery_style': {
            'photography': 'Authentic, diverse individuals in natural settings',
            'illustrations': 'Abstract, calming patterns with gradient overlays',
            'icons': 'Rounded, friendly line icons with consistent stroke width',
            'avoid': 'Stock photos that feel staged, dark or clinical imagery'
        }
    }
    return jsonify(brand_assets)

@media_bp.route('/api/video-script')
def get_video_script():
    """Get promotional video script"""
    video_script = {
        'title': 'Mind Mend - Your AI Mental Health Companion',
        'duration': '90 seconds',
        'scenes': [
            {
                'scene': 1,
                'duration': '0:00-0:10',
                'visual': 'Person looking stressed at computer, then relaxing as they open Mind Mend',
                'voiceover': 'Life can be overwhelming. When you need support, Mind Mend is here.',
                'text_overlay': 'Mental Health Support, Anytime, Anywhere'
            },
            {
                'scene': 2,
                'duration': '0:10-0:25',
                'visual': 'Split screen showing AI conversation and emotion detection',
                'voiceover': 'Our advanced AI therapists understand you. Using multiple AI models, we provide personalized support that adapts to your unique needs.',
                'text_overlay': '7+ Specialized AI Models'
            },
            {
                'scene': 3,
                'duration': '0:25-0:40',
                'visual': 'Various features: video sessions, mood tracking, exercises',
                'voiceover': 'From anxiety to relationships, our platform offers evidence-based therapy, real-time crisis support, and personalized treatment plans.',
                'text_overlay': '24/7 Support • Crisis Intervention • Personalized Care'
            },
            {
                'scene': 4,
                'duration': '0:40-0:55',
                'visual': 'Happy users, progress charts, testimonials',
                'voiceover': 'Join thousands who have transformed their mental health. With a 73% improvement rate, Mind Mend is changing lives every day.',
                'text_overlay': '4.8/5 User Rating • 73% Show Improvement'
            },
            {
                'scene': 5,
                'duration': '0:55-1:30',
                'visual': 'Mind Mend logo with call-to-action',
                'voiceover': 'Your mental health matters. Start your journey today.',
                'text_overlay': 'mindmend.com.au • Start Free Trial'
            }
        ],
        'music': 'Calm, uplifting instrumental with gradual build',
        'style': 'Modern, clean, with purple gradient overlays matching brand'
    }
    return jsonify(video_script)