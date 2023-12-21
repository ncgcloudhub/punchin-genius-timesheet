--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

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
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: core_punchinuser; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.core_punchinuser (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.core_punchinuser OWNER TO postgres;

--
-- Name: core_punchinuser_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.core_punchinuser_groups (
    id bigint NOT NULL,
    punchinuser_id bigint NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.core_punchinuser_groups OWNER TO postgres;

--
-- Name: core_punchinuser_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.core_punchinuser_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_punchinuser_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: core_punchinuser_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.core_punchinuser ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_punchinuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: core_punchinuser_user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.core_punchinuser_user_permissions (
    id bigint NOT NULL,
    punchinuser_id bigint NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.core_punchinuser_user_permissions OWNER TO postgres;

--
-- Name: core_punchinuser_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.core_punchinuser_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_punchinuser_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: core_timeentry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.core_timeentry (
    id bigint NOT NULL,
    clock_in timestamp with time zone NOT NULL,
    clock_out timestamp with time zone,
    user_id bigint NOT NULL,
    description text,
    project character varying(200)
);


ALTER TABLE public.core_timeentry OWNER TO postgres;

--
-- Name: core_timeentry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.core_timeentry ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_timeentry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
1	Admin
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	1	10
11	1	11
12	1	12
13	1	13
14	1	14
15	1	15
16	1	16
17	1	17
18	1	18
19	1	19
20	1	20
21	1	21
22	1	22
23	1	23
24	1	24
25	1	25
26	1	26
27	1	27
28	1	28
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add user	6	add_punchinuser
22	Can change user	6	change_punchinuser
23	Can delete user	6	delete_punchinuser
24	Can view user	6	view_punchinuser
25	Can add time entry	7	add_timeentry
26	Can change time entry	7	change_timeentry
27	Can delete time entry	7	delete_timeentry
28	Can view time entry	7	view_timeentry
\.


--
-- Data for Name: core_punchinuser; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.core_punchinuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$600000$EvlOQL8LNvT7AIN80nPSx7$dSxfqVOTfqSYI5hTQZVi1mqc4mA43gL5NbkjfEBZUcw=	\N	t	admin	Administrator	Account	trionxai@gmail.com	t	t	2023-12-04 21:08:27-05
2	pbkdf2_sha256$600000$aXuqWxlUcjclGVxUvhRz0V$nO6RL3EwWAlQKiIXw4Ox65qxmk+uI/g9s6Dnj6Qk1oU=	2023-12-09 02:08:04.259217-05	t	saiful	Saiful	Bhuiyan	saif.taxpro@outlook.com	t	t	2023-12-04 21:09:18-05
\.


--
-- Data for Name: core_punchinuser_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.core_punchinuser_groups (id, punchinuser_id, group_id) FROM stdin;
1	2	1
\.


--
-- Data for Name: core_punchinuser_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.core_punchinuser_user_permissions (id, punchinuser_id, permission_id) FROM stdin;
\.


--
-- Data for Name: core_timeentry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.core_timeentry (id, clock_in, clock_out, user_id, description, project) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2023-12-05 00:43:48.767726-05	1	Admin	1	[{"added": {}}]	3	2
2	2023-12-05 00:44:49.443277-05	2	saiful	2	[{"changed": {"fields": ["Groups", "First name", "Last name"]}}]	6	2
3	2023-12-05 00:45:06.67719-05	1	admin	2	[{"changed": {"fields": ["First name", "Last name"]}}]	6	2
4	2023-12-05 21:52:40.955983-05	5	nurah	3		6	2
5	2023-12-05 21:52:40.957984-05	4	rita	3		6	2
6	2023-12-05 21:52:40.959024-05	3	demo	3		6	2
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	core	punchinuser
7	core	timeentry
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2023-12-04 21:01:47.504706-05
2	contenttypes	0002_remove_content_type_name	2023-12-04 21:01:47.513356-05
3	auth	0001_initial	2023-12-04 21:01:47.576948-05
4	auth	0002_alter_permission_name_max_length	2023-12-04 21:01:47.58062-05
5	auth	0003_alter_user_email_max_length	2023-12-04 21:01:47.585624-05
6	auth	0004_alter_user_username_opts	2023-12-04 21:01:47.591049-05
7	auth	0005_alter_user_last_login_null	2023-12-04 21:01:47.596495-05
8	auth	0006_require_contenttypes_0002	2023-12-04 21:01:47.599499-05
9	auth	0007_alter_validators_add_error_messages	2023-12-04 21:01:47.604316-05
10	auth	0008_alter_user_username_max_length	2023-12-04 21:01:47.609311-05
11	auth	0009_alter_user_last_name_max_length	2023-12-04 21:01:47.614755-05
12	auth	0010_alter_group_name_max_length	2023-12-04 21:01:47.62075-05
13	auth	0011_update_proxy_permissions	2023-12-04 21:01:47.624757-05
14	auth	0012_alter_user_first_name_max_length	2023-12-04 21:01:47.630377-05
15	core	0001_initial	2023-12-04 21:01:47.71355-05
16	admin	0001_initial	2023-12-04 21:01:47.755255-05
17	admin	0002_logentry_remove_auto_add	2023-12-04 21:01:47.763145-05
18	admin	0003_logentry_add_action_flag_choices	2023-12-04 21:01:47.769135-05
19	sessions	0001_initial	2023-12-04 21:01:47.791093-05
20	core	0002_timeentry_description_timeentry_project	2023-12-05 21:52:26.986022-05
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
qkspwqs2s2miulpb8bxo7h5taborc66t	.eJxVjMsOwiAQRf-FtSE8BhhcuvcbCFNAqgaS0q6M_65NutDtPefcFwtxW2vYRl7CnNiZKXb63ShOj9x2kO6x3TqfeluXmfiu8IMOfu0pPy-H-3dQ46jf2pmCXmgqjshbLEVgdiYqp4XRWgqpMEpvwDqQEpFcAm-TsACetCFg7w-2vjY5:1rAKsx:e5KML5kTP_EvroW6naW1UdUPAxillV6QyBngCwh7_E0	2023-12-18 21:10:07.233524-05
7amwe3xk59utc65kf0mm9q4oo0aqmht6	e30:1rAfoM:PWpCONT7wglCZ_ei6Hni-UQlhJGpRepr1uIYIe6Jx6Y	2023-12-19 19:30:46.489974-05
x58tol53i0dpn0bkiudci4kejmeibrc6	e30:1rAfp0:3BQgCc9iOzkkzOeYFScAfJn651BCvbRZ_u6PJuVNMbQ	2023-12-19 19:31:26.9536-05
5i00n3znrwdr05nauxsnjpoi5ccczt2e	e30:1rAfpv:xBGpeipqkwiN0-CRD5Ni7hx0QJx3hVOJ3hQ8UW8V2ro	2023-12-19 19:32:23.346803-05
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 28, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 28, true);


--
-- Name: core_punchinuser_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.core_punchinuser_groups_id_seq', 1, true);


--
-- Name: core_punchinuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.core_punchinuser_id_seq', 5, true);


--
-- Name: core_punchinuser_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.core_punchinuser_user_permissions_id_seq', 1, false);


--
-- Name: core_timeentry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.core_timeentry_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 6, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 7, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 20, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: core_punchinuser_groups core_punchinuser_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_groups
    ADD CONSTRAINT core_punchinuser_groups_pkey PRIMARY KEY (id);


--
-- Name: core_punchinuser_groups core_punchinuser_groups_punchinuser_id_group_id_44f70eee_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_groups
    ADD CONSTRAINT core_punchinuser_groups_punchinuser_id_group_id_44f70eee_uniq UNIQUE (punchinuser_id, group_id);


--
-- Name: core_punchinuser core_punchinuser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser
    ADD CONSTRAINT core_punchinuser_pkey PRIMARY KEY (id);


--
-- Name: core_punchinuser_user_permissions core_punchinuser_user_pe_punchinuser_id_permissio_7897b7b6_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_user_permissions
    ADD CONSTRAINT core_punchinuser_user_pe_punchinuser_id_permissio_7897b7b6_uniq UNIQUE (punchinuser_id, permission_id);


--
-- Name: core_punchinuser_user_permissions core_punchinuser_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_user_permissions
    ADD CONSTRAINT core_punchinuser_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: core_punchinuser core_punchinuser_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser
    ADD CONSTRAINT core_punchinuser_username_key UNIQUE (username);


--
-- Name: core_timeentry core_timeentry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_timeentry
    ADD CONSTRAINT core_timeentry_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: core_punchinuser_groups_group_id_64317977; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX core_punchinuser_groups_group_id_64317977 ON public.core_punchinuser_groups USING btree (group_id);


--
-- Name: core_punchinuser_groups_punchinuser_id_c5e4e29a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX core_punchinuser_groups_punchinuser_id_c5e4e29a ON public.core_punchinuser_groups USING btree (punchinuser_id);


--
-- Name: core_punchinuser_user_permissions_permission_id_769d885e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX core_punchinuser_user_permissions_permission_id_769d885e ON public.core_punchinuser_user_permissions USING btree (permission_id);


--
-- Name: core_punchinuser_user_permissions_punchinuser_id_00aa1004; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX core_punchinuser_user_permissions_punchinuser_id_00aa1004 ON public.core_punchinuser_user_permissions USING btree (punchinuser_id);


--
-- Name: core_punchinuser_username_af3fbb62_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX core_punchinuser_username_af3fbb62_like ON public.core_punchinuser USING btree (username varchar_pattern_ops);


--
-- Name: core_timeentry_user_id_f1365936; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX core_timeentry_user_id_f1365936 ON public.core_timeentry USING btree (user_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_punchinuser_groups core_punchinuser_gro_punchinuser_id_c5e4e29a_fk_core_punc; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_groups
    ADD CONSTRAINT core_punchinuser_gro_punchinuser_id_c5e4e29a_fk_core_punc FOREIGN KEY (punchinuser_id) REFERENCES public.core_punchinuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_punchinuser_groups core_punchinuser_groups_group_id_64317977_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_groups
    ADD CONSTRAINT core_punchinuser_groups_group_id_64317977_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_punchinuser_user_permissions core_punchinuser_use_permission_id_769d885e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_user_permissions
    ADD CONSTRAINT core_punchinuser_use_permission_id_769d885e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_punchinuser_user_permissions core_punchinuser_use_punchinuser_id_00aa1004_fk_core_punc; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_punchinuser_user_permissions
    ADD CONSTRAINT core_punchinuser_use_punchinuser_id_00aa1004_fk_core_punc FOREIGN KEY (punchinuser_id) REFERENCES public.core_punchinuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_timeentry core_timeentry_user_id_f1365936_fk_core_punchinuser_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.core_timeentry
    ADD CONSTRAINT core_timeentry_user_id_f1365936_fk_core_punchinuser_id FOREIGN KEY (user_id) REFERENCES public.core_punchinuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_core_punchinuser_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_core_punchinuser_id FOREIGN KEY (user_id) REFERENCES public.core_punchinuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--
