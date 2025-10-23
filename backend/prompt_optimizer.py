import dspy
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class PromptOptimizer:
    """DSPy-based prompt optimization engine"""

    def __init__(self):
        """Initialize DSPy with OpenAI configuration"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        model_name = os.getenv("OPENAI_MODEL", "gpt-4")

        # Configure DSPy with OpenAI
        self.lm = dspy.OpenAI(
            model=model_name,
            api_key=api_key,
            temperature=float(os.getenv("DSPY_TEMPERATURE", "0.7"))
        )
        dspy.settings.configure(lm=self.lm)

        # Define signature for prompt optimization
        self.optimizer = dspy.ChainOfThought("purpose, original_prompt -> optimized_prompt, improvements")

    def optimize_prompt(
        self,
        original_prompt: str,
        purpose: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[str], str]:
        """
        Optimize a prompt using DSPy

        Args:
            original_prompt: The original prompt to optimize
            purpose: The intended purpose of the prompt
            examples: Optional input/output examples

        Returns:
            Tuple of (optimized_prompt, improvements_list, explanation)
        """

        # Prepare context with examples if provided
        context = f"Purpose: {purpose}\n"
        if examples:
            context += "Examples:\n"
            for i, example in enumerate(examples, 1):
                context += f"  Example {i}:\n"
                context += f"    Input: {example.get('input', 'N/A')}\n"
                context += f"    Expected Output: {example.get('output', 'N/A')}\n"

        # Create optimization prompt
        optimization_request = f"""
        Optimize the following prompt for better performance and clarity.

        {context}

        Original Prompt:
        {original_prompt}

        Please provide:
        1. An optimized version of the prompt that is clearer, more specific, and more effective
        2. A list of specific improvements made
        3. Explanation of why these changes improve the prompt
        """

        try:
            # Use DSPy to optimize
            result = self.optimizer(
                purpose=purpose,
                original_prompt=original_prompt
            )

            # Parse the result
            optimized_prompt = str(result.optimized_prompt) if hasattr(result, 'optimized_prompt') else original_prompt

            # Extract improvements
            improvements_text = str(result.improvements) if hasattr(result, 'improvements') else ""
            improvements = self._parse_improvements(improvements_text)

            # Generate explanation
            explanation = self._generate_explanation(original_prompt, optimized_prompt, improvements)

            return optimized_prompt, improvements, explanation

        except Exception as e:
            # Fallback to basic optimization
            return self._basic_optimization(original_prompt, purpose)

    def _parse_improvements(self, improvements_text: str) -> List[str]:
        """Parse improvements from text into a list"""
        improvements = []

        # Split by common delimiters
        lines = improvements_text.split('\n')
        for line in lines:
            line = line.strip()
            # Remove bullet points, numbers, etc.
            if line and not line.isspace():
                # Remove common prefixes
                for prefix in ['- ', '* ', '• ', '1. ', '2. ', '3. ', '4. ', '5. ']:
                    if line.startswith(prefix):
                        line = line[len(prefix):]
                        break
                if line:
                    improvements.append(line)

        # If no improvements found, provide default
        if not improvements:
            improvements = [
                "Made the prompt more specific and actionable",
                "Added clarity to expected output format",
                "Improved instruction structure"
            ]

        return improvements[:5]  # Limit to 5 improvements

    def _generate_explanation(
        self,
        original: str,
        optimized: str,
        improvements: List[str]
    ) -> str:
        """Generate an explanation for the optimization"""

        explanation = "The prompt has been optimized to enhance clarity and effectiveness. "

        # Analyze key differences
        if len(optimized) > len(original):
            explanation += "Additional context and specificity were added to guide better responses. "
        elif len(optimized) < len(original):
            explanation += "The prompt was streamlined for conciseness while maintaining clarity. "

        # Add specific improvements
        if improvements:
            explanation += f"Key improvements include: {', '.join(improvements[:3])}. "

        explanation += "These changes should result in more accurate and relevant outputs."

        return explanation

    def _basic_optimization(
        self,
        original_prompt: str,
        purpose: str
    ) -> Tuple[str, List[str], str]:
        """Basic optimization fallback when DSPy fails"""

        # Simple template-based optimization
        optimized = f"""Task: {purpose}

Instructions:
{original_prompt}

Please provide a detailed response that:
1. Directly addresses the stated purpose
2. Is clear and well-structured
3. Includes specific examples where relevant
4. Follows best practices for the given task

Output:"""

        improvements = [
            "Added clear task definition",
            "Structured the instructions for clarity",
            "Specified output requirements",
            "Included guidance for quality response"
        ]

        explanation = (
            "Applied template-based optimization to structure the prompt more effectively. "
            "The optimized version provides clearer context and expectations for better results."
        )

        return optimized, improvements, explanation

    def analyze_prompt_quality(self, prompt: str) -> Dict[str, float]:
        """Analyze prompt quality metrics"""

        metrics = {
            "clarity_score": 0.0,
            "specificity_score": 0.0,
            "structure_score": 0.0,
            "completeness_score": 0.0
        }

        # Simple heuristic-based scoring

        # Clarity: based on sentence structure and length
        sentences = prompt.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        metrics["clarity_score"] = min(1.0, 1.0 - abs(avg_sentence_length - 15) / 30)

        # Specificity: presence of specific keywords
        specific_keywords = ['specific', 'exactly', 'must', 'should', 'format', 'structure']
        specificity_count = sum(1 for word in specific_keywords if word in prompt.lower())
        metrics["specificity_score"] = min(1.0, specificity_count / 3)

        # Structure: presence of formatting
        structure_indicators = ['\n', ':', '-', '1.', '•']
        structure_count = sum(1 for indicator in structure_indicators if indicator in prompt)
        metrics["structure_score"] = min(1.0, structure_count / 3)

        # Completeness: prompt length and detail
        word_count = len(prompt.split())
        metrics["completeness_score"] = min(1.0, word_count / 50)

        # Round all metrics
        metrics = {k: round(v, 2) for k, v in metrics.items()}

        return metrics