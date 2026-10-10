import json
import os
from pathlib import Path

from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.models import GeminiModel
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from flight_agent import understand_request


load_dotenv()


# ---------------------------------------------------------
# Gemini evaluator
# ---------------------------------------------------------

gemini_model = GeminiModel(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)


# ---------------------------------------------------------
# Test data
# ---------------------------------------------------------

with open("evaluation/flight_test_cases.json", "r") as file:
    test_cases = json.load(file)


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

def test_flight_journey_extraction():

    results = []

    for case in test_cases:

        test_id = case["id"]
        user_input = case["user_input"]
        expected = case["expected"]

        # -------------------------------------------------
        # Run SkyAssist agent
        # -------------------------------------------------

        request = understand_request(
            user_message=user_input,
            previous_request=None,
            conversation_history=[]
        )

        actual_output = {
            "intent": request.intent,
            "origin": request.origin,
            "destination": request.destination,
            "departure_date": request.departure_date,
            "adults": request.adults,
            "children": request.children,
            "infants": request.infants
        }

        # -------------------------------------------------
        # Exact / deterministic validation
        # -------------------------------------------------

        field_validation = {
            "intent": actual_output["intent"] == expected["intent"],
            "origin": actual_output["origin"] == expected["origin"],
            "destination": actual_output["destination"] == expected["destination"],
            "departure_date": actual_output["departure_date"] == expected["departure_date"],
            "adults": actual_output["adults"] == expected["adults"],
            "children": actual_output["children"] == expected["children"],
            "infants": actual_output["infants"] == expected["infants"]
        }

        exact_validation = all(field_validation.values())

        # -------------------------------------------------
        # DeepEval test case
        # -------------------------------------------------

        deepeval_test_case = LLMTestCase(
            input=user_input,
            actual_output=json.dumps(actual_output),
            expected_output=json.dumps(expected)
        )

        # -------------------------------------------------
        # GEval — LLM as Judge
        # -------------------------------------------------

        journey_accuracy = GEval(
            name="Flight Journey Accuracy",

            criteria="""
            Evaluate whether the actual output correctly represents
            the flight journey requested by the user.

            Check:

            - intent
            - origin
            - destination
            - departure date
            - adults
            - children
            - infants

            The actual output should match the expected output.

            If a passenger field is null in the expected output,
            the actual output must also keep that field null.

            Do not accept information that was not provided by the user.

            Missing information must not be invented.
            """,

            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],

            threshold=0.8,
            model=gemini_model
        )

        # -------------------------------------------------
        # Run GEval
        # -------------------------------------------------

        journey_accuracy.measure(deepeval_test_case)

        score = journey_accuracy.score
        threshold = journey_accuracy.threshold

        geval_pass = score >= threshold

        # -------------------------------------------------
        # Final result
        # -------------------------------------------------

        final_pass = exact_validation and geval_pass

        results.append({
            "id": test_id,
            "user_input": user_input,
            "expected": expected,
            "actual": actual_output,
            "field_validation": field_validation,
            "exact_validation": exact_validation,
            "geval_score": score,
            "geval_threshold": threshold,
            "geval_pass": geval_pass,
            "final_pass": final_pass,
            "geval_reason": journey_accuracy.reason
        })

        # -------------------------------------------------
        # Console output
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print(f"TEST CASE: {test_id}")
        print("=" * 60)

        print(f"Exact Validation : {'PASS' if exact_validation else 'FAIL'}")
        print(f"GEval Score      : {score:.2f}")
        print(f"GEval Threshold  : {threshold:.2f}")
        print(f"GEval Validation : {'PASS' if geval_pass else 'FAIL'}")
        print(f"Final Result     : {'PASS' if final_pass else 'FAIL'}")

        print("\nExpected:")
        print(json.dumps(expected, indent=2))

        print("\nActual:")
        print(json.dumps(actual_output, indent=2))

        print("\nGEval Reason:")
        print(journey_accuracy.reason)

        print("=" * 60)

        # -------------------------------------------------
        # Pytest assertion
        # -------------------------------------------------

        assert final_pass, (
            f"{test_id} failed. "
            f"Exact validation={exact_validation}, "
            f"GEval score={score:.2f}"
        )
            # -------------------------------------------------
    # Save evaluation results
    # -------------------------------------------------

    results_path = Path("evaluation/evaluation_results.json")

    with open(results_path, "w") as file:
        json.dump(results, file, indent=2)

    print(f"\nEvaluation results saved to: {results_path}")