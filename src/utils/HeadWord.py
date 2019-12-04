def getHeadWord():
    return {
        "Work": ["(Work|WORK)", "(WORK EXPERIENCE|Experience(s?)|EXPERIENCE(S?))", "(History|HISTORY)", "(Projects|PROJECTS)"],
        "Education": ["(Education|EDUCATION)", "(Qualifications|QUALIFICATIONS)"],
        "Skills": [
            "(Skills|SKILLS)",
            "(Proficiency|PROFICIENCY)",
            "LANGUAGE",
            "CERTIFICATION",
            "(Skill ?(sets?)|SKILLSET)"
        ]
    }