import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import csv
from fpdf import FPDF
from io import BytesIO

# Streamlit page config
st.set_page_config(page_title="4th Year Risk Analyser", page_icon="🎓")

# Sidebar Navigation
menu = st.sidebar.selectbox(
    "Choose App Section",
    ["4th Year Analyzer", "View Data Analytics"]
)

if menu == "4th Year Analyzer":

    st.title("🎓 4th Year Risk Analyser")
    st.write("""
    This tool helps you evaluate whether you should proceed with your 4th academic year under the NEP.

    Based on your academic profile, career goals, and personal circumstances, we'll analyse:
    - **Benefits** of doing 4th year
    - **Risks** of doing 4th year
    - A final recommendation
    """)

    st.header("Step 1: Tell us about yourself")

    gpa = st.number_input("Enter your current GPA out of 10:", min_value=0.0, max_value=10.0, step=0.1)
    goal_abroad = st.radio("Do you plan to study abroad after graduation?", ["Yes", "No"])
    research_interest = st.radio("Are you interested in pursuing research further?", ["Yes", "No"])
    placement_interest = st.radio("Do you wish to sit for placements specifically in 4th year?", ["Yes", "No"])
    competitive_exam = st.radio("Are you preparing for any competitive exam (e.g. UPSC)?", ["Yes", "No"])
    internship_experience = st.radio("Do you have any prior internship experience?", ["Yes", "No"])
    financial_stability = st.radio("Is your financial situation stable enough to support an additional year?", ["Yes", "No"])
    solid_job_offer = st.radio("Do you already have a strong job offer from 3rd year placements?", ["Yes", "No"])
    burnout = st.radio("Are you feeling burnt out or uninterested in continuing academics?", ["Yes", "No"])
    no_clear_plan = st.radio("Do you feel unsure about what you'd do in the 4th year and might stay just to avoid a gap?", ["Yes", "No"])
    user_name = st.text_input("Enter your name (optional):")

    submitted = st.button("Analyse My 4th Year Risk")

    if submitted:

        # Scoring logic
        score = 0
        positive_factors = []
        risk_factors = []

        if goal_abroad == "Yes":
            score -= 3
            positive_factors.append("Studying abroad after graduation")

        if research_interest == "Yes":
            score -= 2
            positive_factors.append("Interest in pursuing research further")

        if placement_interest == "Yes":
            score -= 2
            positive_factors.append("Wish to sit for placements in 4th year")

        if competitive_exam == "Yes":
            score -= 2
            positive_factors.append("Intends to use 4th year for preparation of competitive exams")

        if internship_experience == "No":
            score -= 1
            positive_factors.append("No internship experience yet so an extra year could help")

        if financial_stability == "No":
            score += 3
            risk_factors.append("Financial instability to support an additional year")

        if solid_job_offer == "Yes":
            score += 3
            risk_factors.append("Already have a strong job offer from 3rd year placements")

        if burnout == "Yes":
            score += 2
            risk_factors.append("Feeling burnt out or uninterested in continuing academics")

        if no_clear_plan == "Yes":
            score += 3
            risk_factors.append("No clear plan for 4th year and might stay just to avoid a gap")

        if gpa >= 8.0 and internship_experience == "Yes" and solid_job_offer == "Yes":
            score += 2
            risk_factors.append("Strong academic profile with internship and job offer, so 4th year may add limited value")

        name = user_name.strip() if user_name.strip() else "Student"

        st.write("----")
        st.subheader("Your Personalised recommendation for 4th year")

        if score <= 0:
            st.success(f"🎉 Congratulations {name}! Based on your profile, pursuing the 4th year seems beneficial.")
        elif 1 <= score <= 3:
            st.warning(f"⚠️ Think carefully, {name}! It could go either way depending on your priorities and planning.")
        else:
            st.error(f"🚫 Caution {name}! Based on your profile, it may be risky to pursue the 4th year.")

        if positive_factors:
            st.write("**Benefits of doing 4th year ✅**")
            for factor in positive_factors:
                st.write(f"- {factor}")

        if risk_factors:
            st.write("**Risks of doing 4th year ❌**")
            for factor in risk_factors:
                st.write(f"- {factor}")

        # Pie chart
        labels = ['Benefits', 'Risks']
        values = [len(positive_factors), len(risk_factors)]
        colors = ['#4CAF50', '#F44336']

        if sum(values) > 0:
            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            ax.set_title("Your 4th Year Decision Profile")
            st.pyplot(fig)
        else:
            st.write("No benefits or risks identified based on your inputs. Please review your responses.")

        # Save to CSV
        user_data = pd.DataFrame({
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Name": [user_name],
            "GPA": [gpa],
            "Goal Abroad": [goal_abroad],
            "Research Interest": [research_interest],
            "Placement Interest": [placement_interest],
            "Competitive Exam": [competitive_exam],
            "Internship Experience": [internship_experience],
            "Financial Stability": [financial_stability],
            "Solid Job Offer": [solid_job_offer],
            "Burnout": [burnout],
            "No Clear Plan": [no_clear_plan],
            "Score": [score],
            "Positive Factors": [", ".join(positive_factors)],
            "Risk Factors": [", ".join(risk_factors)]
        })

        try:
            user_data.to_csv(
                "user_responses.csv",
                mode='a',
                index=False,
                header=not os.path.exists("user_responses.csv"),
                quoting=csv.QUOTE_ALL,
                encoding='utf-8'
            )
        except Exception as e:
            st.warning(f"Could not save your data to CSV file due to: {e}")
        else:
            st.success("✅ Your responses have been saved successfully!")

        
        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"4th Year Risk Analysis Report for {name}", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"Final Score: {score}\n")
        pdf.multi_cell(0, 10, txt=f"Benefits:\n{', '.join(positive_factors) if positive_factors else 'None'}\n")
        pdf.multi_cell(0, 10, txt=f"Risks:\n{', '.join(risk_factors) if risk_factors else 'None'}\n")

        if score <= 0:
            recommendation = "Recommended to pursue 4th year."
        elif score <= 3:
            recommendation = "Proceed cautiously; depends on your circumstances."
        else:
            recommendation = "It may be risky to pursue 4th year."

        pdf.multi_cell(0, 10, txt=f"Recommendation: {recommendation}")

        # Convert PDF to bytes
        pdf_bytes = pdf.output(dest="S").encode("latin1")

        # Download button
        st.download_button(
            "📅 Download PDF Report",
            data=pdf_bytes,
            file_name=f"{name}_4th_year_report.pdf",
            mime="application/pdf"
        )


elif menu == "View Data Analytics":
    st.title("📊 Data Analytics Dashboard")

    if os.path.exists("user_responses.csv"):
        try:
            df = pd.read_csv(
                "user_responses.csv",
                quoting=csv.QUOTE_ALL,
                encoding='utf-8',
                on_bad_lines='skip'
            )
        except pd.errors.ParserError as e:
            st.error(f"CSV parsing error: {e}")
            df = pd.DataFrame()

        if not df.empty:
            # Convert GPA safely
            df["GPA"] = pd.to_numeric(df["GPA"], errors="coerce")
            df = df.dropna(subset=["GPA"])

            #st.write("### Raw Data Collected")
            #st.dataframe(df)

            st.write("#### GPA Distribution")
            fig1, ax1 = plt.subplots()
            sns.histplot(df["GPA"], bins=10, kde=True, color="skyblue", ax=ax1)
            st.pyplot(fig1)

            st.write("#### How many plan to study abroad?")
            fig2, ax2 = plt.subplots()
            sns.countplot(x="Goal Abroad", data=df, palette="Set2", ax=ax2)
            st.pyplot(fig2)

            st.write("#### Most Common Risk Factors")
            all_risks = []
            for risks in df["Risk Factors"].dropna():
                if isinstance(risks, str) and risks.strip():
                    all_risks.extend(risks.split(", "))
            if all_risks:
                risk_counts = pd.Series(all_risks).value_counts()
                st.bar_chart(risk_counts.head(5))
            else:
                st.info("No risk factors data available yet.")
        else:
            st.info("No valid data found.")
    else:
        st.warning("No data saved yet. Complete some analyses first!")
