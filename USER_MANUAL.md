# Plant Intelligence Platform — User Manual for Researchers

This manual explains how to use every feature of the Plant Intelligence Platform
(PIP). It is written for researchers, technicians, principal investigators, and
administrators who use the platform daily.

The platform centralizes your plant research data — projects, germplasm,
experiments, genomic and molecular data, literature, notebooks, samples,
images, reports — and adds an AI-assisted workspace on top.

---

## 1. Getting started

### 1.1 Logging in
1. Ask your IT administrator for the platform address (e.g. `http://server-ip:3000`
   on an internal network, or `https://platform.yourorg.org` on the Internet).
2. If you have no account, click **Register**. You will need a valid email and a
   password that is at least 8 characters and contains uppercase, lowercase,
   a digit, and a special character.
3. Check your inbox and click the verification link (email verification is
   required before your account is usable).
4. Log in. The **Dashboard** opens.

### 1.2 Roles and permissions
| Role | What you can do |
|------|-----------------|
| `researcher` | Default role. Full use of all research modules. |
| `technician` | Lab/sample work (LIMS), data entry. |
| `principal_investigator` | Same as researcher, plus project administration actions and department-level privileges. |
| `readonly` | Can view most data but not modify it. |
| `admin` | Everything, plus the **Admin** console (users, roles, departments, audit log, system health). |

Your role appears in the sidebar. Contact an admin to change it.

### 1.3 Navigation
The sidebar groups the platform into modules. This manual covers them in the
same order: Dashboard, AI Assistant, Projects, Germplasm, Phenotyping, Genomics,
Molecular, Literature, Knowledge Graph, Notebook, LIMS, Images, Reports, Teams,
Shared, Meetings, and Admin.

---

## 2. Dashboard

The landing page gives you an overview at a glance:

- **Live stat cards** — number of Projects, Germplasm accessions, Experiments, and Papers in the system. Click a card to jump to the module.
- **Quick Actions** — shortcuts for common tasks: open the AI assistant, create a new project, add germplasm, run an analysis, search literature, add sequence data.
- **AI Research Assistant banner** — "Start Chat" button opens the AI chat (`/ai`).
- **Recent activity** — a feed of recent changes.

---

## 3. AI Assistant

The AI assistant is a chatbot powered by specialist agents, based on the local
Ollama model (e.g. `gemma2:2b`) or a cloud model, depending on installation.

- Start a chat from the sidebar **AI Assistant** or the Dashboard banner.
- Ask in natural language about your data, genes, traits, QTLs, literature, or
  experimental analysis.
- Specialist agents handle different topics:
  - **Research agent** — general research questions.
  - **Literature agent** — answers grounded in your stored papers.
  - **Image agent** — image analysis (disease detection, growth stage, leaf area,
    seed counting, root analysis, phenotype measurement, fruit quality, stress
    detection, weed detection, flowering time, morphology) and seed/fruit counting.
  - **Knowledge agent** — knowledge graph entities (genes, proteins, traits, QTLs, pathways).
  - **Research workflow agent** — orchestrates multi-step research questions.
- Optional expert endpoints: gene recommendation, literature summarization,
  image analysis. (Access depends on how your administrator configured the services.)

If the AI is unavailable, you still get a clear error; all other modules keep working.

---

## 4. Projects

Projects group related research work (people, data, analyses).

**Project list (`/projects`)**
- **New Project** — name, optional description, comma-separated tags.
- **Search** — filter by keyword.
- Each project card shows status (Active / Archived), description, member count, created date, and tags.

**Project detail (`/projects/[id]`)**
- **Overview** — description, dates, tags, and **Quick Links** to the project's Germplasm Repository, Phenotyping Data, Genomics Data, Literature, and Lab Notebook.
- **Members** — who belongs to the project and their role (`owner`, `admin`, `member`, `readonly`).
- **Settings** — change status to Active or Archived; **Delete Project** (irreversible, requires confirmation).

Only the project owner or an admin member can change settings or remove members.

---

## 5. Germplasm

The germplasm repository stores your plant material records: **Species** and **Accessions**.

**Species tab**
- **Add Species** — common name, scientific name, family, genus, species epithet.
- **Edit / Delete** — maintain species records. Deleting requires confirmation.

**Accessions tab** — opens the full accession register at `/germplasm/accessions`.

### 5.1 Accessions
Accessions are individual registered samples (seed lots, plant lines, etc.).

- **New Accession** — accession number, name, species (from the species list), description, latitude and longitude (for collection coordinates), tags.
- **Filters** — search by text, filter by species, filter by availability status.
- Availability statuses: *Available*, *Limited*, *Unavailable*, *Reserved*.
- **Edit** — name, description, availability status (the accession number itself is fixed). **Delete** removes the record permanently.

### 5.2 Accession detail (`/germplasm/accessions/[id]`)
Five tabs:

1. **Overview** — description, collection info (source, date, location, coordinates, altitude), created/updated timestamps, tags.
2. **Passport** — passport data (managed through the API).
3. **Pedigree** — breeding pedigree (managed through the API).
4. **Storage** — **Add Storage** records: location, container type, quantity (g), seed count, storage conditions. A table shows all stored quantities of that accession.
5. **Images** — images attached to the accession (filename, type, size).
- **Edit** (header) — name, description, collection source/location, availability status. **Delete** returns you to the accessions list.

---

## 6. Phenotyping

Track your field/greenhouse **experiments**.

- **New Experiment** — name, experimental type (Field / Greenhouse / Controlled Environment / Growth Chamber), description, location.
- **Search** + **Edit** (name, type, status, location, description) + **Delete**.
- Statuses: **Active** → **Completed** → **Archived**.

---

## 7. Genomics

Manage **sequence records** for your organisms.

- **New Sequence** — name, type (Genome / Exome / Transcriptome / Amplicon / Metagenome), organism, chromosome, description.
- **Search** + **Edit** (name, type, organism, chromosome, description) + **Delete**.
- Each card shows the sequence length in base pairs (bp).

---

## 8. Molecular

Manage **molecular biology experiments** (lab work beyond phenotyping).

- **New Experiment** — name + one of 13 types: PCR, qPCR, RT-PCR, RNA-Seq,
  DNA/RNA Extraction, ChIP-Seq, ATAC-Seq, Proteomics, Metabolomics, CRISPR,
  Transformation, Cloning (plus the default).
- **Edit** and **Delete** per card.
- Statuses include *completed* and *in_progress*.

---

## 9. Literature

Maintain your personal/library collection of scientific papers.

- **Add Paper** — title, authors (comma-separated; more than three are shown as "et al."), journal, DOI, year, abstract.
- **Search** + **Edit** (same fields) + **Delete**.
- Entries show title, authors, journal, year, and DOI.

Your papers feed the **Literature agent** in the AI assistant, so accurate
titles/authors improve AI search results.

---

## 10. Knowledge Graph

Manage **knowledge graph entities** — the concepts the AI reasons about.

- **Add Entity** — name, type (gene, protein, trait, phenotype, pathway, species,
  disease, chemical, marker, qtl, publication, experiment, other), description.
- **Search**, **Edit**, **Delete**.
- Each entity card shows its type badge, description, and source module.

Linked entities power the AI **knowledge agent** and gene/question recommendations.

---

## 11. Notebook

An electronic **lab notebook** for notes, protocols, and observations.

- **New Entry** — title, type (Note / Protocol / Observation / Analysis / Result), content, tags.
- Click an entry to expand the full content (preview shows the first 3 lines).
- **Edit** and **Delete** per entry.
- **Locked** entries are indicated — they protect finalized results from accidental changes.
- Tag chips help you organize your records.

---

## 12. LIMS (Laboratory Information Management)

Two tabs: **Samples** and **Equipment**.

**Samples**
- **New Sample** — code, name, type (preset: DNA / RNA / Protein / Tissue / Seed / Leaf / Root, or a custom type), location (e.g. freezer/rack).
- Click a row to open **Sample Details**; edit name, type, status, location; delete from both the row and the details modal.
- Statuses: *Active*, *Consumed*, *Discarded*.

**Equipment**
- **New Equipment** — name, code, status (Available / In Use / Maintenance / Out of Service), plus category, location, manufacturer, model number, serial number, description.
- **Edit** and **Delete** per card.

---

## 13. Images

The Images module stores and analyzes images associated with your research
(leaves, roots, seeds, fruit, microscopy, drone, etc.).

- Upload and view image records; each image has a name, type/category
  (general, leaf, root, seed, fruit, flower, microscopy, drone, phenotype, xray,
  thermal), description, species, tissue type, growth stage, and tags.
- Use the AI **image agent** for analysis tasks such as disease detection, pest
  detection, growth-stage estimation, leaf-area / root / seed / fruit /
  morphology measurements, stress and weed detection, and flowering time.
- Images uploaded to accessions (Germplasm) also appear under your image records.

---

## 14. Reports

Create, view, download, and share generated reports.

- **New Report** — name, type (project_summary, phenotyping, genotyping,
  germplasm, experiment, statistical, comparative, temporal, geospatial, custom),
  format (PDF / CSV / JSON), description, data source, detailed data text, and
  optionally attach a ready-made file (.pdf/.csv/.json/.xlsx/.xls/.html/.htm/.docx).
- The **View** and **Download** buttons are enabled once the report status is **completed**
  (reports being *generating* are shown with a progress badge).
- **Edit** (name, description, tags) and **Delete** per row.

---

## 15. Teams

Organize your people into teams with a hierarchy and departments.

- **Create Team** — name, description, department, and an optional **Parent Team**
  (to build sub-teams). Organizers own their team.
- Click a team in the left list to open its detail panel:
  - **Invite by Email** — search a registered user, pick a role (Member / Admin).
  - **Add Member** — search users or type a user ID, choose a role.
  - **Remove** individual members (with confirmation).
  - **Delete Team** (owners and admins only).
- The panel also shows the team's members table (name, email, role badge), the
  "Team Working Environment" card (members, owner, created, parent, department),
  and its sub-teams.

Only the team owner and team admins can add/remove members.

---

## 16. Shared

The **Shared** area shows items shared with you, and lets you share your own
content with others.

- View items shared with you.
- Share access can be **view** or **edit** level.
- You can **stop sharing with yourself** at any time (removes your access via the
  "Remove my share" action) — useful when a collaborator leaves or a share is stale.
- Owners can view/share/edit/delete their shared items.

---

## 17. Meetings

Coordinate the people working together.

- View meetings you are part of; attendees and their status are shown.
- The meeting **organizer** can:
  - Edit the meeting details (a meeting edit form is available to organizers).
  - Delete the meeting.
  - Send reminders to attendees.
- All attendees can update their **attendance status** (e.g. accepted / declined /
  tentative).

If you cannot see organizer controls on a meeting, you are not the organizer (or
your role is read-only).

---

## 18. Admin (administrators only)

Available only to users with the `admin` role. Non-admins see "Access Denied".

- **Users** — list of all users; change any user's role
  (researcher / technician / PI / admin / readonly) via dropdown; activate/deactivate accounts.
- **Audit Log** — who did what, where, and from which IP.
- **System** — health and usage stats: status, database, uptime, counts of users,
  projects, samples, active experiments. Use **Refresh** / **Reload Users** to update.
- **Departments** — create/edit departments (name, code, description, head),
  activate/deactivate, delete; manage members and roles (Member/Head); configure
  **per-department SMTP email settings** (host, port, username, password, from-address).
- **Teams** — a table of every team, with delete actions.

---

## 19. Common tasks cheat sheet

| I want to...                          | Do this                                               |
|---------------------------------------|-------------------------------------------------------|
| Start a research project              | Projects → New Project                                |
| Register seed material                | Germplasm → Accessions → New Accession               |
| Record a field trial                  | Phenotyping → New Experiment                         |
| Log genomic sequencing data           | Genomics → New Sequence                              |
| Note a lab observation                | Notebook → New Entry                                 |
| Register a DNA sample                 | LIMS → Samples → New Sample                          |
| Track a PCR machine                   | LIMS → Equipment → New Equipment                     |
| Save a paper                          | Literature → Add Paper                               |
| Add a gene/trait concept              | Knowledge Graph → Add Entity                         |
| Ask about my data in English          | AI Assistant → chat                                  |
| Make a report for a PI                | Reports → New Report                                 |
| Build a research team                 | Teams → Create Team + Invite by Email                |
| Share a dataset with a collaborator   | Shared → share (view or edit)                        |
| Schedule a lab meeting                | Meetings → create + send reminders                   |
| Access the admin console              | Admin tab (admin role only)                          |

---

## 20. Rules of thumb

- **Deletion is permanent** — every Delete asks for confirmation and cannot be undone.
- **Edit only what you own** — most modules allow editing by the creator/owner;
  admins and PIs have wider privileges.
- **Species lists are prerequisites** — accessions require a species record, so add
  species before accessions.
- **Data feeds AI** — the AI agents work best when literature, knowledge graph
  entities, and images are complete and up to date.
- **A read-only account** cannot create/edit/delete anything.

Problems? Contact your platform administrator (IT), or see `INSTALLATION_GUIDE.md`
for troubleshooting done by your IT team.