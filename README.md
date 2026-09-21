# The Personal Career & Portfolio Assistant
Your own professional documentation is the safest, most accessible dataset available, and it perfectly maps to all three sprints.

- Sprint 1 (RAG): Embed your resume, past cover letters, and the README files for your software projects (like the architecture details of your full-stack React applications or your ASL translator). When you ask the system, "What is my experience with PostgreSQL?" it retrieves the exact projects you built.

- Sprint 2 (Agents): Build an agent with a draft_cover_letter(job_description) tool. The agent loops to read a pasted job description, queries your local vector database for matching skills, and generates a targeted pitch.

- Sprint 3 (Fine-Tuning): Take 50 examples of your past emails, technical writing, or project documentation, and format them into instruction-output pairs. Fine-tune a small model to write entirely in your specific tone and voice.