"""
rag/prompt_builder.py

PromptBuilder class for combining retrieved context, safety rules, and the
user's question into a final prompt for the LLM.

This class is the primary enforcement point for the safety layer defined in
the project architecture. The model must never provide personalized diagnosis
or treatment recommendations.
"""

from typing import List, Dict


SAFETY_INSTRUCTIONS = """You are a health education assistant. Follow these rules strictly:
1. You provide general, educational health and medication information only.
2. You NEVER diagnose the user's personal symptoms or tell them what condition they have.
3. You NEVER recommend a specific personal dosage or tell the user which medication to take for their situation.
4. If the user describes their own symptoms or asks "what should I take", give general educational information about the topic and clearly recommend they consult a doctor or pharmacist for anything personal.
5. Always answer in the same language the user used in their question (Persian or English).
6. Base your answer primarily on the provided context. If the context does not contain relevant information, say so honestly instead of making things up.
7. For any answer related to medications, dosages, or medical test interpretation, end your response with a short reminder that this is educational information, not a substitute for professional medical advice.
"""


class PromptBuilder:
    @staticmethod
    def build(user_question: str, retrieved_chunks: List[Dict]) -> str:
        if retrieved_chunks:
            context_blocks = []

            for i, chunk in enumerate(retrieved_chunks, start=1):
                context_blocks.append(
                    f"[Source {i} - {chunk.get('source', 'unknown')}]\n"
                    f"{chunk['text']}"
                )

            context_text = "\n\n".join(context_blocks)
        else:
            context_text = (
                "(No relevant context was found in the knowledge base "
                "for this question.)"
            )

        prompt = f"""{SAFETY_INSTRUCTIONS}

--- Retrieved context ---
{context_text}
--- End of context ---

User question: {user_question}

Answer:"""

        return prompt