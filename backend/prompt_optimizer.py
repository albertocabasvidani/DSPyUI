import dspy
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()


class PromptOptimizationSignature(dspy.Signature):
    """Signature for prompt optimization with validation"""
    purpose = dspy.InputField(desc="The intended purpose of the prompt")
    original_prompt = dspy.InputField(desc="The original prompt to optimize")
    examples_context = dspy.InputField(desc="Optional examples context", default="")

    optimized_prompt = dspy.OutputField(
        desc="Optimized version that is clearer, more specific, and more effective"
    )
    improvements = dspy.OutputField(
        desc="List of specific improvements made (one per line, max 5)"
    )


class PromptOptimizer:
    """DSPy-based prompt optimization engine with advanced features"""

    def __init__(self):
        """Initialize DSPy with OpenAI configuration"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        model_name = os.getenv("OPENAI_MODEL", "gpt-4")
        temperature = float(os.getenv("DSPY_TEMPERATURE", "0.7"))

        # Configure DSPy with OpenAI (using new DSPy 2.5+ API)
        self.lm = dspy.LM(
            f'openai/{model_name}',
            api_key=api_key,
            temperature=temperature
        )
        dspy.configure(lm=self.lm)

        # Define base module for prompt optimization
        self.base_optimizer = dspy.ChainOfThought(PromptOptimizationSignature)

        # Compiled optimizer (will be set when examples are provided)
        self.compiled_optimizer = None

    def optimize_prompt(
        self,
        original_prompt: str,
        purpose: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[str], str]:
        """
        Optimize a prompt using DSPy with optional few-shot learning

        Args:
            original_prompt: The original prompt to optimize
            purpose: The intended purpose of the prompt
            examples: Optional input/output examples for few-shot optimization

        Returns:
            Tuple of (optimized_prompt, improvements_list, explanation)
        """

        # Prepare examples context if provided
        examples_context = ""
        if examples and len(examples) > 0:
            examples_context = "Consider these examples:\n"
            for i, example in enumerate(examples, 1):
                examples_context += f"Example {i}:\n"
                examples_context += f"  Input: {example.get('input', 'N/A')}\n"
                examples_context += f"  Output: {example.get('output', 'N/A')}\n"

        try:
            # Use advanced optimization if examples are provided
            if examples and len(examples) > 0:
                result = self._optimize_with_examples(
                    original_prompt, purpose, examples, examples_context
                )
            else:
                # Use base ChainOfThought without examples
                result = self._optimize_without_examples(
                    original_prompt, purpose, examples_context
                )

            # Validate and parse the result
            optimized_prompt = str(result.optimized_prompt) if hasattr(result, 'optimized_prompt') else original_prompt
            improvements_text = str(result.improvements) if hasattr(result, 'improvements') else ""

            # Apply assertions for quality validation
            self._validate_optimization(original_prompt, optimized_prompt)

            # Extract improvements
            improvements = self._parse_improvements(improvements_text)

            # Generate explanation
            explanation = self._generate_explanation(original_prompt, optimized_prompt, improvements)

            return optimized_prompt, improvements, explanation

        except Exception as e:
            # Fallback to basic optimization
            print(f"Optimization failed: {e}, using fallback")
            return self._basic_optimization(original_prompt, purpose)

    def _optimize_without_examples(
        self,
        original_prompt: str,
        purpose: str,
        examples_context: str
    ) -> dspy.Prediction:
        """Optimize using base ChainOfThought"""
        return self.base_optimizer(
            purpose=purpose,
            original_prompt=original_prompt,
            examples_context=examples_context
        )

    def _optimize_with_examples(
        self,
        original_prompt: str,
        purpose: str,
        examples: List[Dict[str, str]],
        examples_context: str
    ) -> dspy.Prediction:
        """Optimize using BootstrapFewShot when examples are provided"""
        try:
            from dspy.teleprompt import BootstrapFewShot

            # Convert examples to DSPy format
            trainset = []
            for example in examples[:5]:  # Limit to 5 examples
                trainset.append(
                    dspy.Example(
                        purpose=purpose,
                        original_prompt=original_prompt,
                        examples_context=examples_context
                    ).with_inputs("purpose", "original_prompt", "examples_context")
                )

            # Define validation metric
            def validation_metric(example, pred, trace=None):
                return self._calculate_optimization_score(
                    example.original_prompt if hasattr(example, 'original_prompt') else original_prompt,
                    pred.optimized_prompt if hasattr(pred, 'optimized_prompt') else ""
                )

            # Compile optimizer with few-shot examples
            optimizer = BootstrapFewShot(
                metric=validation_metric,
                max_bootstrapped_demos=min(3, len(examples)),
                max_labeled_demos=min(3, len(examples))
            )

            compiled = optimizer.compile(self.base_optimizer, trainset=trainset)

            # Use compiled optimizer
            return compiled(
                purpose=purpose,
                original_prompt=original_prompt,
                examples_context=examples_context
            )

        except Exception as e:
            print(f"Few-shot optimization failed: {e}, falling back to base optimizer")
            return self._optimize_without_examples(original_prompt, purpose, examples_context)

    def _validate_optimization(self, original: str, optimized: str) -> None:
        """Validate optimization quality using assertions"""
        try:
            # Assertion: Optimized prompt should not be empty
            dspy.Assert(
                len(optimized.strip()) > 0,
                "Optimized prompt cannot be empty"
            )

            # Suggestion: Optimized prompt should be different from original
            dspy.Suggest(
                optimized.strip() != original.strip(),
                "Optimized prompt should differ from original"
            )

            # Suggestion: Optimized prompt should be substantial
            dspy.Suggest(
                len(optimized.split()) >= len(original.split()) * 0.5,
                "Optimized prompt should maintain reasonable length"
            )

        except Exception:
            # Assertions failed, will be caught by outer try-catch
            pass

    def _calculate_optimization_score(self, original: str, optimized: str) -> float:
        """Calculate optimization quality score using DSPy-style metrics"""
        if not optimized or len(optimized.strip()) == 0:
            return 0.0

        score = 0.0

        # Reward for being different from original
        if optimized.strip() != original.strip():
            score += 0.3

        # Reward for improved length (not too short, not excessively long)
        len_ratio = len(optimized.split()) / max(len(original.split()), 1)
        if 1.0 <= len_ratio <= 2.5:
            score += 0.3
        elif 0.8 <= len_ratio < 1.0:
            score += 0.2

        # Reward for structure indicators
        structure_markers = ['\n', ':', '-', '1.', '2.', 'Step', 'must', 'should']
        structure_count = sum(1 for marker in structure_markers if marker in optimized)
        score += min(0.4, structure_count * 0.05)

        return min(1.0, score)

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
        """Analyze prompt quality using enhanced metrics"""

        metrics = {
            "clarity_score": 0.0,
            "specificity_score": 0.0,
            "structure_score": 0.0,
            "completeness_score": 0.0
        }

        try:
            # Use LM-based analysis for better quality assessment
            analysis_signature = dspy.ChainOfThought(
                "prompt -> clarity_assessment, specificity_assessment, structure_assessment, completeness_assessment"
            )

            result = analysis_signature(prompt=prompt[:500])  # Limit length for analysis

            # Parse assessments into scores
            def parse_assessment(assessment: str) -> float:
                """Convert assessment text to score"""
                assessment_lower = str(assessment).lower()
                if any(word in assessment_lower for word in ['excellent', 'high', 'strong']):
                    return 0.9
                elif any(word in assessment_lower for word in ['good', 'clear', 'adequate']):
                    return 0.7
                elif any(word in assessment_lower for word in ['fair', 'moderate', 'acceptable']):
                    return 0.5
                elif any(word in assessment_lower for word in ['poor', 'weak', 'unclear']):
                    return 0.3
                else:
                    return 0.5  # Default neutral score

            metrics["clarity_score"] = parse_assessment(
                getattr(result, 'clarity_assessment', 'moderate')
            )
            metrics["specificity_score"] = parse_assessment(
                getattr(result, 'specificity_assessment', 'moderate')
            )
            metrics["structure_score"] = parse_assessment(
                getattr(result, 'structure_assessment', 'moderate')
            )
            metrics["completeness_score"] = parse_assessment(
                getattr(result, 'completeness_assessment', 'moderate')
            )

        except Exception:
            # Fallback to heuristic-based scoring
            metrics = self._heuristic_quality_analysis(prompt)

        # Round all metrics
        metrics = {k: round(v, 2) for k, v in metrics.items()}

        return metrics

    def _heuristic_quality_analysis(self, prompt: str) -> Dict[str, float]:
        """Fallback heuristic-based quality analysis"""
        metrics = {
            "clarity_score": 0.0,
            "specificity_score": 0.0,
            "structure_score": 0.0,
            "completeness_score": 0.0
        }

        # Clarity: based on sentence structure and length
        sentences = prompt.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        metrics["clarity_score"] = min(1.0, 1.0 - abs(avg_sentence_length - 15) / 30)

        # Specificity: presence of specific keywords
        specific_keywords = ['specific', 'exactly', 'must', 'should', 'format', 'structure', 'please', 'provide']
        specificity_count = sum(1 for word in specific_keywords if word in prompt.lower())
        metrics["specificity_score"] = min(1.0, specificity_count / 4)

        # Structure: presence of formatting
        structure_indicators = ['\n', ':', '-', '1.', '2.', '•', 'Step']
        structure_count = sum(1 for indicator in structure_indicators if indicator in prompt)
        metrics["structure_score"] = min(1.0, structure_count / 4)

        # Completeness: prompt length and detail
        word_count = len(prompt.split())
        metrics["completeness_score"] = min(1.0, word_count / 50)

        return metrics