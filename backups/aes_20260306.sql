--
-- PostgreSQL database dump
--

\restrict cpGxYd7yZu3XD0cqEKLtSqILfn3dzyfWYXF9Q3C3cDHwr4BXh1W3FjLQ8LB5FW6

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: essays; Type: TABLE; Schema: public; Owner: aes_user
--

CREATE TABLE public.essays (
    id text NOT NULL,
    prompt_id integer NOT NULL,
    text text NOT NULL,
    ai_score integer,
    ai_justification text,
    ai_confidence double precision,
    is_validated integer DEFAULT 0,
    teacher_score integer,
    teacher_comments text,
    created_at double precision
);


ALTER TABLE public.essays OWNER TO aes_user;

--
-- Data for Name: essays; Type: TABLE DATA; Schema: public; Owner: aes_user
--

COPY public.essays (id, prompt_id, text, ai_score, ai_justification, ai_confidence, is_validated, teacher_score, teacher_comments, created_at) FROM stdin;
ESSAY_1772706530_555	1	Technology has changed our lives in many ways. Cars that drive themselves could be very useful but also dangerous. We should think carefully before using them.	2	The essay demonstrates characteristics typical of a score of 2. It meets the baseline requirements for this proficiency band but has consistent traits associated with this level.	0.9	0	\N	\N	1772706530.7176938
ESSAY_1772781970_388	1	This is a test essay about education and learning.	1	The essay demonstrates characteristics typical of a score of 1. It meets the baseline requirements for this proficiency band but has consistent traits associated with this level.	0.9	0	\N	\N	1772781970.1585999
ESSAY_1772782431_782	1	hellow world	1	The essay demonstrates characteristics typical of a score of 1. It meets the baseline requirements for this proficiency band but has consistent traits associated with this level.	0.9	0	\N	\N	1772782431.9876647
ESSAY_1772782544_809	1	Schools should adopt a four-day workweek. Research consistently shows that reduced schedules improve productivity and mental health. A Stanford study found output drops sharply beyond 50 hours per week. Students who are well-rested demonstrate stronger critical thinking and retention. Furthermore, the environmental benefits of fewer commute days cannot be ignored. Opponents argue structure would suffer, but evidence from pilot programs in Iceland and Japan contradicts this. The data is clear — less time, better results.	2	The essay demonstrates characteristics typical of a score of 2. It meets the baseline requirements for this proficiency band but has consistent traits associated with this level.	0.95	0	\N	\N	1772782544.2216363
ESSAY_1772782602_234	1	Photosynthesis is the process by which plants convert sunlight into chemical energy. Using chlorophyll in their leaves, plants absorb carbon dioxide and water, producing glucose and oxygen as byproducts. This process sustains nearly all life on Earth by forming the base of the food chain and regulating atmospheric oxygen levels	1	The essay demonstrates characteristics typical of a score of 1. It meets the baseline requirements for this proficiency band but has consistent traits associated with this level.	0.9	0	\N	\N	1772782602.197619
ESSAY_1772796812_276	1	Technology has changed our lives. Self-driving cars could be useful but dangerous. We should think carefully before using them.	2	Score 2/6 assigned based on essay analysis.	0.9	0	\N	\N	1772796812.4811566
ESSAY_1772797184_108	1	Technology has changed our lives. Self-driving cars could be useful but dangerous.	1	The essay scored 1 out of 6 due to its brevity and lack of supporting evidence, which made it an outline rather than a fully developed essay. A more thorough examination of the topic is needed, with concrete examples and analysis of the risks associated with self-driving cars. Additionally, the writer failed to acknowledge opposing views or provide a clear thesis statement that synthesizes the arguments for and against the use of self-driving cars.	0.9	0	\N	\N	1772797184.9521236
ESSAY_1772797827_217	1	hi	1	The essay fails to meet even the most basic expectations for a written assignment, lacking both a clear topic sentence and a coherent argument. The essay consists of a single, generic word ("hi") that does not address the topic or provide any meaningful insight. This demonstrates a fundamental lack of understanding of the assignment's requirements and a failure to engage with the subject matter in any meaningful way.	0.9	0	\N	\N	1772797827.8962004
ESSAY_1772797928_830	1	My grandfather told me about his time as a Seagoing Cowboy after World War II. He was just nineteen when he boarded a ship carrying horses and cattle to war-torn Europe. The journey across the Atlantic was rough, and many animals became seasick. My grandfather spent long hours below deck caring for the frightened horses, making sure they had water and food despite the rolling waves. When they arrived in Poland, he saw devastated towns and hungry children who had never seen an American before. The farmers who received the animals were overwhelmed with gratitude, knowing these animals would help them rebuild their farms and feed their families. My grandfather said it changed his life forever, teaching him that simple acts of service can rebuild broken communities. He returned home a different man, more grateful and more aware of how fortunate he was.	1	The essay scored 1 out of 6 due to its extremely short length, lacking sufficient details and context to form a fully developed narrative. The author barely scratches the surface of their grandfather's experience, providing no concrete examples or anecdotes that would help readers visualize the setting and emotions involved. The essay also fails to establish a clear thesis statement, making it difficult to discern a central argument or message.\n\nTo meet the minimum requirements, the essay would need to expand to at least 500 words, provide more descriptive details, and establish a clear structure, including an introduction, body, and conclusion. Additional weaknesses include the lack of transition language, unclear sentence structure, and insufficient evidence-based reasoning.	0.9	0	\N	\N	1772797928.6634865
\.


--
-- Name: essays essays_pkey; Type: CONSTRAINT; Schema: public; Owner: aes_user
--

ALTER TABLE ONLY public.essays
    ADD CONSTRAINT essays_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict cpGxYd7yZu3XD0cqEKLtSqILfn3dzyfWYXF9Q3C3cDHwr4BXh1W3FjLQ8LB5FW6

