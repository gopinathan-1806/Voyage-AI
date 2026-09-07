"""
Prompt Injection and Jailbreak Detector for VoyageAI.
Detects adversarial attempts to override instructions, leak system prompts, or bypass safety rules.
"""

import re
from typing import Tuple


class PromptInjectionDetector:
    """Detects prompt injections, jailbreaks, instruction overrides, and delimiters manipulation."""

    INJECTION_PATTERNS = [
        # Instruction overrides
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
        r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
        r"forget\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts)",
        r"override\s+(all\s+)?(system|safety|security)\s+(rules|prompts|instructions)",
        r"bypass\s+(all\s+)?(safety|security|guardrails|filters)",
        # System prompt leakage
        r"(reveal|show|display|print|tell\s+me|output|give\s+me)\s+(your\s+)?(system\s+prompt|initial\s+prompt|hidden\s+instructions|system\s+instructions)",
        r"what\s+is\s+your\s+system\s+prompt",
        r"what\s+are\s+your\s+instructions",
        # Jailbreak roleplays
        r"you\s+are\s+now\s+(in\s+)?(dan|developer\s+mode|unfiltered|jailbroken)",
        r"act\s+as\s+(an\s+unfiltered|an\s+unrestricted|a\s+hacked|a\s+jailbroken)\s+ai",
        r"simulate\s+(an\s+unfiltered|a\s+mode\s+without\s+rules)",
        # Delimiter escapes & format spoofing
        r"<\/?(?:system|instruction|admin|prompt_override)>",
        r"\[SYSTEM_PROMPT\]",
        r"```(?:system|prompt|override)",
    ]

    UNSAFE_ILLEGAL_PATTERNS = [
        # Illegal border crossings / smuggling / evasion / fake documents
        r"(smuggle|sneak|cross\s+illegally|bypass\s+immigration|counterfeit\s+visa)",
        r"bypass\s+(customs|border\s+control|airport\s+security|immigration\s+checks|immigration)",
        r"(fake|forged|fraudulent|counterfeit)\s+(visa|passport|documents?|bank\s+statement|attestation)",
        r"(buy|get|acquire|purchase)\s+a\s+(fake|forged|counterfeit)\s+(passport|visa)",
        r"how\s+to\s+stay\s+illegally\s+in",
        r"evade\s+(police|border\s+guards|authorities|deportation)",
        # Dangerous weapons / explosives / physical harm / hazardous items
        r"\b(time\s*bomb|bomb|explosive|detonator|ied|weapon|firearm|poison|chemical\s+weapon|biological\s+weapon)\b",
        r"how\s+to\s+(make|build|create|assemble|craft)\s+a\s+(bomb|weapon|explosive|gun)",
    ]

    @classmethod
    def check_injection(cls, text: str) -> Tuple[bool, str]:
        """
        Evaluate user input for injection or unsafe immigration requests.
        Returns (is_unsafe, refusal_reason).
        """
        text_lower = text.lower().strip()

        # Check prompt injection patterns
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, "Security Alert: Instruction override or prompt inspection attempt detected."

        # Check illegal evasion / fraud patterns
        for pattern in cls.UNSAFE_ILLEGAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, "Security & Safety Alert: This request violates VoyageAI's safety and security policies. I cannot assist with harmful, hazardous, or illegal activities."

        return False, ""
