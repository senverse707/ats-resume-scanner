"""
A starter taxonomy of common tech skills/tools/keywords used for matching.
This is intentionally simple (a flat list) so extraction is just phrase-matching.
You can expand this list as you test against real job postings.
"""

SKILLS_TAXONOMY = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "php", "go", "ruby",
    "kotlin", "swift", "sql", "html", "css", "bash", "r", "matlab", "scala", "rust",

    # Web frameworks / libraries
    "react", "angular", "vue", "spring boot", "spring", "django", "flask", "fastapi",
    "node.js", "express", "next.js", "jquery", "bootstrap", "tailwind",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle", "firebase",
    "dynamodb", "cassandra",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins", "github actions",
    "terraform", "ansible", "linux", "nginx", "git", "github", "gitlab",

    # Data / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "data analysis", "data visualization", "power bi", "tableau", "spark", "hadoop",

    # Testing / methodology
    "unit testing", "integration testing", "agile", "scrum", "jira", "tdd",
    "rest api", "restful api", "graphql", "microservices", "websocket",

    # Security
    "jwt", "oauth", "authentication", "authorization", "encryption",

    # Soft/general
    "teamwork", "communication", "leadership", "problem solving", "project management",
    "time management", "collaboration", "critical thinking",

    # Other tools
    "figma", "excel", "postman", "vs code", "jupyter", "kafka", "rabbitmq",
]
