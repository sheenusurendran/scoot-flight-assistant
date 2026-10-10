import json
from pathlib import Path
from html import escape


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

results_file = BASE_DIR / "evaluation_results.json"
report_file = BASE_DIR / "report" / "flight_test_report.html"
report_file.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Load evaluation results
# ---------------------------------------------------------

with open(results_file, "r") as file:
    results = json.load(file)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

total = len(results)
passed = sum(1 for result in results if result["final_pass"])
failed = total - passed

pass_percentage = (passed / total * 100) if total else 0


# ---------------------------------------------------------
# Build detailed test sections
# ---------------------------------------------------------

test_sections = ""

for result in results:

    test_id = result["id"]
    user_input = result["user_input"]

    expected = result["expected"]
    actual = result["actual"]

    field_validation = result["field_validation"]

    exact_validation = result["exact_validation"]
    geval_pass = result["geval_pass"]
    final_pass = result["final_pass"]

    geval_score = result["geval_score"]
    geval_threshold = result["geval_threshold"]

    geval_reason = result["geval_reason"]

    final_status = "PASS" if final_pass else "FAIL"
    final_class = "pass" if final_pass else "fail"

    # -----------------------------------------------------
    # Expected / Actual JSON
    # -----------------------------------------------------

    expected_json = escape(
        json.dumps(expected, indent=2)
    )

    actual_json = escape(
        json.dumps(actual, indent=2)
    )

    # -----------------------------------------------------
    # Field validation table
    # -----------------------------------------------------

    validation_rows = ""

    for field, passed_field in field_validation.items():

        expected_value = expected.get(field)
        actual_value = actual.get(field)

        expected_display = escape(
            json.dumps(expected_value)
        )

        actual_display = escape(
            json.dumps(actual_value)
        )

        field_status = "PASS" if passed_field else "FAIL"
        field_class = "pass" if passed_field else "fail"

        validation_rows += f"""
        <tr>
            <td><strong>{escape(field)}</strong></td>
            <td><code>{expected_display}</code></td>
            <td><code>{actual_display}</code></td>
            <td class="{field_class}">
                {field_status}
            </td>
        </tr>
        """

    # -----------------------------------------------------
    # Test case section
    # -----------------------------------------------------

    test_sections += f"""

    <div class="test-case">

        <div class="test-header">

            <div>
                <h2>{escape(test_id)}</h2>

                <p class="user-input">
                    <strong>User Input:</strong>
                    {escape(user_input)}
                </p>
            </div>

            <div class="{final_class} final-status">
                {final_status}
            </div>

        </div>


        <!-- Expected and Actual JSON -->

        <h3>Expected JSON vs Actual JSON</h3>

        <div class="json-container">

            <div class="json-box">

                <h4>Expected JSON</h4>

                <pre>{expected_json}</pre>

            </div>


            <div class="json-box">

                <h4>Actual JSON</h4>

                <pre>{actual_json}</pre>

            </div>

        </div>


        <!-- Field Validation -->

        <h3>Field-by-Field Validation</h3>

        <table>

            <thead>

                <tr>
                    <th>Field</th>
                    <th>Expected</th>
                    <th>Actual</th>
                    <th>Validation</th>
                </tr>

            </thead>

            <tbody>

                {validation_rows}

            </tbody>

        </table>


        <!-- Validation Summary -->

        <h3>Validation Summary</h3>

        <div class="validation-summary">

            <p>
                <strong>Exact JSON Validation:</strong>

                <span class="{
                    'pass' if exact_validation else 'fail'
                }">
                    {
                        'PASS' if exact_validation else 'FAIL'
                    }
                </span>
            </p>


            <p>
                <strong>GEval Score:</strong>
                {geval_score:.2f}
            </p>


            <p>
                <strong>GEval Threshold:</strong>
                {geval_threshold:.2f}
            </p>


            <p>
                <strong>GEval Validation:</strong>

                <span class="{
                    'pass' if geval_pass else 'fail'
                }">
                    {
                        'PASS' if geval_pass else 'FAIL'
                    }
                </span>
            </p>


            <p>
                <strong>Final Result:</strong>

                <span class="{final_class}">
                    {final_status}
                </span>
            </p>

        </div>


        <!-- GEval Reason -->

        <h3>GEval Reason</h3>

        <div class="reason">
            {escape(geval_reason)}
        </div>

    </div>

    """


# ---------------------------------------------------------
# HTML
# ---------------------------------------------------------

html = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>SkyAssist Flight AI Evaluation Report</title>


<style>

body {{

    font-family: Arial, sans-serif;

    margin: 40px;

    background: #f5f7fa;

    color: #222;

}}


h1 {{

    margin-bottom: 5px;

}}


.subtitle {{

    color: #666;

    margin-bottom: 30px;

}}


.summary {{

    display: flex;

    gap: 20px;

    margin-bottom: 40px;

    flex-wrap: wrap;

}}


.card {{

    background: white;

    padding: 20px;

    border-radius: 10px;

    min-width: 150px;

    box-shadow: 0 2px 8px rgba(0,0,0,0.08);

}}


.card h2 {{

    margin: 0;

    font-size: 28px;

}}


.card p {{

    margin: 5px 0 0;

    color: #666;

}}


.pass {{

    color: #16803c;

    font-weight: bold;

}}


.fail {{

    color: #c62828;

    font-weight: bold;

}}


.test-case {{

    background: white;

    margin-bottom: 35px;

    padding: 30px;

    border-radius: 12px;

    box-shadow: 0 2px 8px rgba(0,0,0,0.08);

}}


.test-header {{

    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    margin-bottom: 25px;

}}


.test-header h2 {{

    margin-top: 0;

}}


.final-status {{

    font-size: 20px;

    padding: 8px 16px;

    border-radius: 6px;

}}


.user-input {{

    color: #555;

}}


.json-container {{

    display: flex;

    gap: 20px;

    flex-wrap: wrap;

}}


.json-box {{

    flex: 1;

    min-width: 350px;

}}


pre {{

    background: #f1f3f5;

    padding: 20px;

    border-radius: 8px;

    overflow-x: auto;

    font-size: 14px;

}}


table {{

    width: 100%;

    border-collapse: collapse;

    margin-top: 10px;

}}


th, td {{

    padding: 12px;

    border-bottom: 1px solid #ddd;

    text-align: left;

}}


th {{

    background: #eeeeee;

}}


code {{

    background: #f1f3f5;

    padding: 4px 7px;

    border-radius: 4px;

}}


.validation-summary {{

    background: #f8f9fa;

    padding: 15px 20px;

    border-radius: 8px;

}}


.reason {{

    background: #f8f9fa;

    padding: 20px;

    border-radius: 8px;

    line-height: 1.6;

}}


</style>

</head>


<body>


<h1>SkyAssist Flight AI Evaluation Report</h1>

<div class="subtitle">

LLM Journey Extraction &amp; DeepEval Evaluation

</div>


<!-- Summary -->

<div class="summary">

    <div class="card">

        <h2>{total}</h2>

        <p>Total Tests</p>

    </div>


    <div class="card">

        <h2 class="pass">{passed}</h2>

        <p>Passed</p>

    </div>


    <div class="card">

        <h2 class="fail">{failed}</h2>

        <p>Failed</p>

    </div>


    <div class="card">

        <h2>{pass_percentage:.0f}%</h2>

        <p>Pass Rate</p>

    </div>

</div>


<h2>Detailed Test Results</h2>


{test_sections}


</body>

</html>

"""


# ---------------------------------------------------------
# Write report
# ---------------------------------------------------------

with open(report_file, "w") as file:

    file.write(html)


print("HTML report generated successfully:")

print(report_file)
