from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import List

from .config import ChannelConfig, FounderProfile, load_founder_profile
from .feedback import social_visual_feedback_specs
from .models import GeneratedAssets, GuestProfile, VideoDetails
from .utils import compact_whitespace, timestamp_label


def build_assets(channel: ChannelConfig, details: VideoDetails) -> GeneratedAssets:
    profile = load_founder_profile()
    guest = infer_guest(details)
    transcript_text = build_transcript_text(details)
    summary_text = build_summary(details, transcript_text)
    theme = detect_theme(details, summary_text)
    hook_bank = build_hook_bank(channel.language, details, summary_text, theme, profile)
    linkedin_hashtags, x_hashtags, instagram_hashtags = build_platform_hashtags(channel.language, details, theme)
    linkedin_post = build_linkedin_post(
        channel.language, details, summary_text, hook_bank[0], theme, profile, linkedin_hashtags
    )
    x_post = build_x_post(channel.language, details, summary_text, hook_bank[0], theme, x_hashtags)
    instagram_post = build_instagram_post(channel.language, details, summary_text, hook_bank[0], theme, instagram_hashtags)
    image_prompt, image_specs = build_image_brief(channel.language, details, summary_text, theme, profile)
    thank_you_subject, thank_you_email = build_thank_you_email(channel.language, details, guest)
    notes = build_notes(details, guest)
    return GeneratedAssets(
        summary_text=summary_text,
        hook_bank=hook_bank,
        linkedin_post=linkedin_post,
        linkedin_hashtags=linkedin_hashtags,
        x_post=x_post,
        x_hashtags=x_hashtags,
        instagram_post=instagram_post,
        instagram_hashtags=instagram_hashtags,
        image_prompt=image_prompt,
        image_specs=image_specs,
        thank_you_subject=thank_you_subject,
        thank_you_email=thank_you_email,
        notes=notes,
    )


def infer_guest(details: VideoDetails) -> GuestProfile:
    title = details.summary.title
    searchable = " ".join([title, details.description])
    patterns = [
        r"\bwith (?P<name>[A-Z][A-Za-z.\-]+(?: [A-Z][A-Za-z.\-]+){0,3})",
        r"\bavec (?P<name>[A-Z][A-Za-z.\-]+(?: [A-Z][A-Za-z.\-]+){0,3})",
        r"\bi sit down with (?P<name>[A-Z][A-Za-z.\-]+(?: [A-Z][A-Za-z.\-]+){0,3})",
        r"\bconversation with (?P<name>[A-Z][A-Za-z.\-]+(?: [A-Z][A-Za-z.\-]+){0,3})",
    ]
    for pattern in patterns:
        match = re.search(pattern, searchable)
        if match:
            return GuestProfile(name=match.group("name").strip(), detected_from="title")
    if "interview" in title.lower() or "podcast" in title.lower():
        return GuestProfile(name=None, detected_from="interview_without_name")
    return GuestProfile(name=None, detected_from="host_only_or_unknown")


def build_transcript_text(details: VideoDetails) -> str:
    if not details.transcript:
        return compact_whitespace(details.description)
    return compact_whitespace(" ".join(snippet.text for snippet in details.transcript))


def build_summary(details: VideoDetails, transcript_text: str) -> str:
    description_lines = [
        normalize_terms(compact_whitespace(line).replace("👉", ""))
        for line in details.description.splitlines()
        if compact_whitespace(line)
        and "http" not in line
        and not compact_whitespace(line).startswith("#")
        and len(compact_whitespace(line)) > 20
    ]
    if description_lines:
        core = description_lines[:3]
        return " ".join(core)
    sentences = [normalize_terms(sentence) for sentence in split_sentences(transcript_text)]
    return " ".join(sentences[:3])


def build_hook_bank(
    language: str,
    details: VideoDetails,
    summary_text: str,
    theme: str,
    profile: FounderProfile,
) -> List[str]:
    primary = first_meaningful_sentence(summary_text)
    if theme == "decision":
        if language == "fr":
            return [
                "Tu crois voir clair. Et c'est peut-être justement là que le danger commence.",
                "Cette vidéo parle d'un piège discret en bipolarité : prendre une décision au moment où tout te semble évident.",
                "Certaines décisions ne détruisent pas une journée. Elles déplacent toute une vie.",
                "Avant de quitter, casser, acheter ou annoncer quelque chose, il y a une question à se poser.",
                primary,
            ]
        return [
            "The worst time to make a life decision might be the moment you feel the most certain.",
            "This episode looks at a quiet trap in bipolarity: confusing certainty with clarity.",
            "Some decisions do not ruin a day. They redirect a whole life.",
            "Before you quit, buy, break, or announce something big, pause here first.",
            primary,
        ]
    if theme == "aging":
        if language == "fr":
            return [
                "On parle souvent du diagnostic. Beaucoup moins de ce que devient la bipolarité avec l'âge.",
                "Vieillir avec une bipolarité, ce n'est pas juste continuer pareil plus longtemps.",
                "Certaines questions deviennent plus importantes avec l'âge : sommeil, traitements, autonomie, entourage.",
                "Ce sujet est rarement visible, alors qu'il concerne l'avenir de beaucoup de personnes.",
                primary,
            ]
        return [
            "We talk a lot about diagnosis. Much less about what bipolarity looks like as people grow older.",
            "Growing older with bipolarity is not just the same story repeated for longer.",
            "Age changes the conversation: sleep, treatment, autonomy, relationships, and long-term support.",
            "This is an under-discussed mental health topic that deserves much more attention.",
            primary,
        ]
    if language == "fr":
        return [
            "On n'a pas besoin de plus de bruit. On a besoin de plus de clarte utile.",
            "Quand on parle depuis le vecu, un sujet complexe peut redevenir concret.",
            "Parler de bipolarite avec precision, c'est deja proteger un peu plus de stabilite.",
            primary,
            f"Chez {profile.organization}, ce sujet merite plus qu'un slogan. Il merite une vraie conversation.",
        ]
    return [
        "Some topics need less noise and more useful clarity.",
        "When you start from lived experience, a complex subject becomes easier to name and discuss.",
        "Talking about bipolarity with precision can protect stability and reduce stigma at the same time.",
        primary,
        f"At {profile.organization}, this subject deserves more than a slogan. It deserves a real conversation.",
    ]


def build_linkedin_post(
    language: str,
    details: VideoDetails,
    summary_text: str,
    hook: str,
    theme: str,
    profile: FounderProfile,
    hashtags: List[str],
) -> str:
    notes = minute_notes(details)
    summary_sentence = normalize_terms(summary_text)
    bullets, closing_question = linkedin_scaffold(language, theme)
    credibility_line = founder_credibility_line(language, profile)
    if language == "fr":
        body = [
            hook,
            "",
            f"Dans cette nouvelle vidéo HopeStage, on parle d'un sujet central : {summary_sentence}",
            "",
            credibility_line,
            "",
            notes[0] if notes else fallback_note(language, theme),
            "",
            "Ce que je retiens :",
            *[f"• {item}" for item in bullets],
            "",
            closing_question,
            "",
            f"Vidéo : {details.summary.url}",
            "",
            " ".join(hashtags),
        ]
        return "\n".join(body)
    body = [
        hook,
        "",
        f"In this week's HopeStage video, we focus on a core question: {summary_sentence}",
        "",
        credibility_line,
        "",
        notes[0] if notes else fallback_note(language, theme),
        "",
        "What stood out to me:",
        *[f"• {item}" for item in bullets],
        "",
        closing_question,
        "",
        f"Video: {details.summary.url}",
        "",
        " ".join(hashtags),
    ]
    return "\n".join(body)


def build_x_post(
    language: str,
    details: VideoDetails,
    summary_text: str,
    hook: str,
    theme: str,
    hashtags: List[str],
) -> str:
    if theme == "decision":
        if language == "fr":
            candidate = (
                "Tu te sens ultra clair ? C'est parfois le pire moment pour prendre une grande décision. "
                "En bipolarité, une nuit de sommeil et un regard extérieur peuvent t'éviter une erreur très chère. "
                f"{details.summary.url} {' '.join(hashtags)}"
            )
        else:
            candidate = (
                "Feeling unusually certain can be the worst moment to make a big decision. "
                "With bipolarity, one night of sleep and outside perspective can prevent a very expensive mistake. "
                f"{details.summary.url} {' '.join(hashtags)}"
            )
    elif theme == "aging":
        if language == "fr":
            candidate = (
                "On parle beaucoup du diagnostic. Beaucoup moins de ce que devient la bipolarité avec l'âge. "
                "Sommeil, routine, soutien, autonomie: la conversation doit évoluer. "
                f"{details.summary.url} {' '.join(hashtags)}"
            )
        else:
            candidate = (
                "We talk a lot about diagnosis. Much less about what bipolarity looks like with age. "
                "Sleep, routine, support, autonomy: the conversation needs to evolve. "
                f"{details.summary.url} {' '.join(hashtags)}"
            )
    else:
        if language == "fr":
            candidate = f"{hook} {details.summary.url} {' '.join(hashtags)}"
        else:
            candidate = f"{hook} {details.summary.url} {' '.join(hashtags)}"
    return trim_to_limit(candidate, 280)


def build_instagram_post(
    language: str,
    details: VideoDetails,
    summary_text: str,
    hook: str,
    theme: str,
    hashtags: List[str],
) -> str:
    if theme == "decision":
        if language == "fr":
            lines = [
                "Tu te sens très sûr de toi ?",
                "Ce n'est pas toujours un feu vert.",
                "",
                "En bipolarité, la sensation de clarté peut être le moment le plus risqué.",
                "Dors. Respire. Reviens-y demain.",
            ]
        else:
            lines = [
                "You feel unusually certain?",
                "That is not always a green light.",
                "",
                "With bipolarity, clarity can be the most dangerous feeling.",
                "Sleep first. Decide later.",
            ]
    elif theme == "aging":
        if language == "fr":
            lines = [
                "On parle trop peu",
                "de la bipolarité qui avance en âge.",
                "",
                "Le sommeil, la routine et le soutien changent tout.",
                "Ce sujet mérite une vraie place.",
            ]
        else:
            lines = [
                "We talk too little",
                "about growing older with bipolarity.",
                "",
                "Sleep, routine, and support matter even more over time.",
                "This topic deserves more space.",
            ]
    else:
        lines = [hook, "", first_meaningful_sentence(summary_text)]
    lines.extend(["", " ".join(hashtags)])
    return "\n".join(lines)


def build_platform_hashtags(
    language: str,
    details: VideoDetails,
    theme: str,
) -> tuple[List[str], List[str], List[str]]:
    base = base_hashtags(language)
    topic = topic_hashtags(language, details, theme)
    linkedin = dedupe_hashtags(base["linkedin"] + topic[:3])
    x = dedupe_hashtags(base["x"] + topic[:2])
    instagram = dedupe_hashtags(base["instagram"] + topic[:5])
    return linkedin, x, instagram


def base_hashtags(language: str) -> dict[str, List[str]]:
    if language == "fr":
        return {
            "linkedin": ["#bipolarite", "#santementale", "#hopestage", "#psychoeducation"],
            "x": ["#bipolarite", "#santementale", "#hopestage"],
            "instagram": ["#bipolarite", "#santementale", "#hopestage", "#psychoeducation", "#stabilite"],
        }
    return {
        "linkedin": ["#bipolarity", "#mentalhealth", "#hopestage", "#psychoeducation"],
        "x": ["#bipolarity", "#mentalhealth", "#hopestage"],
        "instagram": ["#bipolarity", "#mentalhealth", "#hopestage", "#psychoeducation", "#stability"],
    }


def topic_hashtags(language: str, details: VideoDetails, theme: str) -> List[str]:
    haystack = strip_accents(" ".join([details.summary.title, details.description]).lower())
    tags: List[str] = []
    if theme == "decision":
        tags.extend(["#priseDeDecision", "#prevention"] if language == "fr" else ["#decisionmaking", "#prevention"])
    if theme == "aging":
        tags.extend(["#vieillissement", "#soutien"] if language == "fr" else ["#aging", "#support"])
    keyword_map = [
        ("aah", "#aah"),
        ("work", "#work"),
        ("travail", "#travail"),
        ("sleep", "#sleep"),
        ("sommeil", "#sommeil"),
        ("addiction", "#addiction"),
        ("pregnan", "#grossesse" if language == "fr" else "#pregnancy"),
        ("postpartum", "#postpartum"),
        ("genetic", "#genetique" if language == "fr" else "#genetics"),
        ("genet", "#genetique" if language == "fr" else "#genetics"),
        ("children", "#parents" if language == "fr" else "#parenting"),
        ("enfant", "#parents"),
    ]
    for needle, tag in keyword_map:
        if needle in haystack:
            tags.append(tag)
    return dedupe_hashtags(tags)


def dedupe_hashtags(tags: List[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for tag in tags:
        normalized = tag.lower()
        if not normalized.startswith("#"):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(tag)
    return deduped


def build_image_brief(
    language: str,
    details: VideoDetails,
    summary_text: str,
    theme: str,
    profile: FounderProfile,
) -> tuple[str, List[str]]:
    palette = palette_summary(profile)
    direction = profile.visual_direction.lower()
    if theme == "decision":
        if language == "fr":
            prompt = (
                "Portrait éditorial minimaliste d'une personne devant deux chemins, tension intérieure calme, "
                f"lumiere douce, palette {palette}, ambiance HopeStage, {direction}, sans texte, composition avec zone sure centrale."
            )
        else:
            prompt = (
                "Minimal editorial portrait of a person facing two paths, calm inner tension, soft light, "
                f"palette {palette}, HopeStage tone, {direction}, no text, centered safe area for social crops."
            )
    elif theme == "aging":
        if language == "fr":
            prompt = (
                "Portrait éditorial chaleureux d'une personne plus âgée dans une lumière naturelle, "
                f"ambiance stable et digne, palette {palette}, {direction}, sans texte, style magazine sante mentale."
            )
        else:
            prompt = (
                "Warm editorial portrait of an older adult in natural light, stable and dignified mood, "
                f"palette {palette}, {direction}, no text, mental-health magazine style."
            )
    else:
        prompt = (
            "Editorial social image with calm natural light, human-centered composition, "
            f"palette {palette}, {direction}, no text, strong central safe area for multiple social crops."
        )
    specs = social_visual_feedback_specs()
    return prompt, specs


def build_thank_you_email(language: str, details: VideoDetails, guest: GuestProfile) -> tuple[str, str]:
    if guest.detected_from == "host_only_or_unknown":
        if language == "fr":
            return (
                "Aucun invité détecté",
                "\n".join(
                    [
                        "Aucun invité externe n'a été détecté automatiquement pour cette vidéo.",
                        "Vérifie si c'est un épisode solo avant d'envoyer un email de remerciement.",
                    ]
                ),
            )
        return (
            "No guest detected",
            "\n".join(
                [
                    "No external guest was detected automatically for this video.",
                    "Check whether this is a solo episode before sending a thank-you email.",
                ]
            ),
        )
    if language == "fr":
        subject = "Merci pour ton échange avec HopeStage"
        opener = f"Bonjour {guest.name}," if guest.name else "Bonjour,"
        body = [
            opener,
            "",
            "Merci encore d'avoir pris le temps de participer à cette conversation avec HopeStage.",
            "L'échange était clair, généreux et utile. Il va vraiment aider d'autres personnes à prendre du recul, à mieux comprendre leur bipolarité et à se sentir moins seules.",
            "",
            f"La vidéo est maintenant en ligne : {details.summary.url}",
            "",
            "Si tu veux, je peux aussi te partager les extraits ou les posts que nous allons préparer autour de cet échange.",
            "",
            "Merci encore pour ta confiance,",
            "Clément",
            "HopeStage",
        ]
        if not guest.name:
            body.insert(3, "Le prénom de la personne invitée n'a pas été détecté automatiquement. Pense à personnaliser l'ouverture avant envoi.")
        return subject, "\n".join(body)
    subject = "Thank you for joining HopeStage"
    opener = f"Hi {guest.name}," if guest.name else "Hi,"
    body = [
        opener,
        "",
        "Thank you again for taking the time to join this conversation with HopeStage.",
        "The exchange was generous, grounded, and genuinely useful. It will help more people understand bipolarity with more clarity and less stigma.",
        "",
        f"The video is now live: {details.summary.url}",
        "",
        "If helpful, I can also share the clips or draft posts we prepare around the episode.",
        "",
        "Thank you again,",
        "Clément",
        "HopeStage",
    ]
    if not guest.name:
        body.insert(3, "The guest name was not detected automatically, so the greeting should be personalized before sending.")
    return subject, "\n".join(body)


def build_notes(details: VideoDetails, guest: GuestProfile) -> List[str]:
    notes = []
    if not details.transcript_available:
        notes.append("Transcript was not available, so copy was generated from title and description only.")
    if guest.detected_from != "title":
        notes.append("Guest name should be checked manually before sending the thank-you email.")
    notes.extend(minute_notes(details)[:3])
    return notes


def minute_notes(details: VideoDetails) -> List[str]:
    buckets = defaultdict(list)
    for snippet in details.transcript:
        buckets[int(snippet.start // 60)].append(snippet.text)
    notes = []
    for minute in sorted(buckets)[:5]:
        text = compact_whitespace(" ".join(buckets[minute]))
        if not text:
            continue
        notes.append(f"[{minute:02d}:00] {text[:220].rstrip()}...")
    return notes


def founder_credibility_line(language: str, profile: FounderProfile) -> str:
    if language == "fr":
        return (
            f"J'aborde ce sujet avec un double regard : le vecu, environ {profile.stable_years} ans de stabilite, "
            "et des centaines d'echanges avec psychiatres et personnes concernees."
        )
    return (
        f"I approach this through both lived experience and pattern recognition: around {profile.stable_years} years of "
        "stability, hundreds of conversations with psychiatrists, and many discussions with people living with bipolarity."
    )


def palette_summary(profile: FounderProfile) -> str:
    preferred_order = [
        "elephant_green",
        "pale_goldenrod",
        "biloba_flower",
        "mint_tulip",
        "dull_orange",
        "dark",
        "white",
    ]
    color_names = [name.replace("_", " ") for name in preferred_order if name in profile.design_palette]
    return ", ".join(color_names)


def split_sentences(text: str) -> List[str]:
    return [compact_whitespace(part) for part in re.split(r"(?<=[.!?])\s+", text) if compact_whitespace(part)]


def first_meaningful_sentence(text: str) -> str:
    for sentence in split_sentences(text):
        if len(sentence) >= 50:
            return sentence
    return normalize_terms(compact_whitespace(text))


def detect_theme(details: VideoDetails, summary_text: str) -> str:
    haystack = normalize_terms(" ".join([details.summary.title, details.description, summary_text])).lower()
    if any(token in haystack for token in ["decision", "décision", "quit", "demission", "divorce"]):
        return "decision"
    if any(token in haystack for token in ["grow older", "older", "ageing", "aging", "geriatric"]):
        return "aging"
    return "general"


def linkedin_scaffold(language: str, theme: str) -> tuple[List[str], str]:
    if theme == "decision":
        if language == "fr":
            return (
                [
                    "le sentiment de clarté n'est pas toujours fiable",
                    "le sommeil et le niveau d'activation changent la qualité d'une décision",
                    "demander un regard extérieur peut éviter une erreur lourde",
                ],
                "Question simple à garder : est-ce que cette décision me semble toujours juste demain, après du sommeil et du recul ?",
            )
        return (
            [
                "certainty is not the same as clarity",
                "sleep and activation level change decision quality",
                "outside perspective can prevent expensive mistakes",
            ],
            "A useful question to keep close: will this decision still feel right tomorrow, after sleep and perspective?",
        )
    if theme == "aging":
        if language == "fr":
            return (
                [
                    "le vieillissement change concrètement la manière de parler de bipolarité",
                    "la stabilité à long terme dépend aussi de sommeil, de routine et d'ajustements réalistes",
                    "on manque encore de conversations accessibles sur l'avancée en âge",
                ],
                "Question utile : qu'est-ce qui devient plus important pour protéger la stabilité quand on avance en âge ?",
            )
        return (
            [
                "age changes the practical conversation around bipolarity",
                "long-term stability depends on sleep, routine, and realistic support",
                "we still do not talk enough about bipolarity across the full lifespan",
            ],
            "Useful question: what becomes more important for stability as someone grows older?",
        )
    if language == "fr":
        return (
            [
                "le sujet mérite plus de nuance et moins de raccourcis",
                "les expériences vécues demandent des mots simples et précis",
                "une bonne conversation peut déjà réduire une partie du stigma",
            ],
            "Question utile : quelle idée de cette vidéo mérite d'être gardée pour la semaine ?",
        )
    return (
        [
            "the topic deserves more nuance and less noise",
            "lived experience needs simple and precise language",
            "a better conversation can already reduce stigma",
        ],
        "Useful question: what is one idea from this video worth carrying into the week?",
    )


def fallback_note(language: str, theme: str) -> str:
    if theme == "decision":
        return (
            "Le point central : une grande décision mérite du recul, surtout quand tout paraît urgent."
            if language == "fr"
            else "The central point: a major decision deserves distance, especially when everything feels urgent."
        )
    if theme == "aging":
        return (
            "Le point central : on parle trop peu de ce que devient la bipolarité avec l'âge."
            if language == "fr"
            else "The central point: we still talk far too little about what bipolarity looks like with age."
        )
    return (
        "Le point central : cette vidéo met de la clarté sur une expérience souvent mal comprise."
        if language == "fr"
        else "The central point: this video adds clarity to an experience that is often misunderstood."
    )


def normalize_terms(text: str) -> str:
    normalized = compact_whitespace(text)
    normalized = normalized.replace("bipolar disorder", "bipolarity")
    normalized = normalized.replace("Bipolar disorder", "Bipolarity")
    normalized = normalized.replace("trouble bipolaire", "bipolarité")
    return normalized


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def trim_to_limit(text: str, limit: int) -> str:
    compact = compact_whitespace(text)
    if len(compact) <= limit:
        return compact
    shortened = compact[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,.;:-")
    return shortened + "…"
