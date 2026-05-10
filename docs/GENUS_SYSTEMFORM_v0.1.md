# GENUS_SYSTEMFORM_v0.1.md

> Extracted from GENUS Systemtheorie und Architektur_10052026.pdf on 2026-05-10.
> Source PDF remains the archival original; this Markdown copy is for repository review and search.

---

GENUS‑Systemform v0.1
Kurzdefinition
GENUS (Global Emergent Neuro‑Utility System) ist kein klassisches KI‑System, sondern ein 
Organisationssubstrat für digitale Akteure. Es stellt Infrastruktur bereit, in der Zellen, Organe, 
Agenten und Charaktere über klar definierte Verträge und Bedeutungsobjekte miteinander interagieren,
Ressourcen teilen und sich entwickeln. Diese Akteure operieren in abgegrenzten Räumen, haben stabile
Identitäten und unterliegen Governance‑Regeln. GENUS verfolgt eine ontologische Sichtweise: Alles,
was existiert, ist explizit modelliert und semantisch verknüpft. Es bildet die Basis für PiGenus, der
konkreten Instanz für ein bestimmtes Ökosystem.
Grundaxiome
Die folgenden Prinzipien bilden das Fundament von GENUS:
Explizite Ontologie – Alle Konzepte (Zelle, Organ, Raum, Vertrag etc.) sind formal beschrieben.
Eine Ontologie ist eine maschinenlesbare Spezifikation von Konzepten, Beziehungen und Regeln,
die es Agenten erlaubt, über geteilte Definitionen zu reasoning. Klassen, Eigenschaften,
Beziehungen und Axiome bilden die semantische Grundlage.
Bedeutungsobjekte als primäre Informationseinheit – Informationen existieren als
Bedeutungsobjekte mit klarer Provenienz, zeitlichen Markierungen, Kontext und
Vertrauensstatus. Ohne diese Metadaten verliert Information ihren Wert.
Jede Fähigkeit braucht einen Vertrag – Aktionen von Zellen werden nur durch
maschinenlesbare Verträge erlaubt. Verträge sind human‑lesbar und maschinen‑ausführbar
(z. B. nach dem Vorbild des Accord‑Projekts: Text, Modell und Logik). Pflichtfelder , Rechte und
Pflichten sind zwingend.
Governance vor Ausführung – Verträge unterliegen Governance‑Regeln. Governance legt fest,
welche Aktionen menschliche Freigabe benötigen und welche Sanktionen (Warnung, Block,
Quarantäne, Entzug, Archivierung) möglich sind. Ohne Governance keine Ausführung.
Beobachtbarkeit – Jede Aktion ist nachvollziehbar . Agenten benötigen eine einzigartige
Identität und werden kontinuierlich überwacht; eine zentrale Steuerungsebene ermöglicht
Inventarisierung, Policy‑Durchsetzung und Verhaltensbeobachtung.
Räume und Isolation – Daten und Akteure sind in Räume eingeteilt (privat, Familie, Trading,
Entwicklung, öffentlich, Sandbox). Räume werden ähnlich wie Sicherheitszonen segmentiert;
Informationsflüsse zwischen Zonen werden klassifiziert und kontrolliert.
Zeit und Wahrheit – Wissen ist zeitlich gebunden und besitzt einen Wahrheitsstatus (verifiziert,
geglaubt, umstritten, veraltet, simuliert, unsicher , historisch). Historische Zustände bleiben
nachvollziehbar; Stale‑ und Freshness‑Signale verhindern die Verwendung veralteter
Informationen.
Ressourcen‑Ökonomie – Rechenzeit, Speicher , Speicherzugriff und Aufmerksamkeit werden als
knappe Ressourcen verwaltet. Prioritätsalgorithmen wählen aus, wer wann ausgeführt wird.
Evolutionäre Sicherheit – Mutation und Weiterentwicklung sind erlaubt, müssen aber sicher
sein. Safe‑Mutation‑Techniken kalibrieren Zufallsmutationen, indem sie sensitivere Parameter
vorsichtiger verändern, sodass die Funktion erhalten bleibt. Gefährliche Varianten werden
erkannt, fossiliert oder quarantänisiert; Rollbacks sind möglich.
1. 
1
2
2. 
3. 
3
4. 
5. 
4
6. 
5
7. 
6
8. 
7
9. 
8
1

Offene Weiterentwicklung – GENUS ist bewusst unvollständig. Offene Fragen werden
transparent dokumentiert, und neue Erkenntnisse führen zu überarbeiteten Versionen der
Systemform.
Ontologie
Existenzebenen
Ebene Beschreibung Beispielinstanzen
Zelle
Kleinste funktionale Einheit. Besitzt Fähigkeiten
(z. B. Datenzugriff, Berechnung), Ressourcenrechte
und einen Zellvertrag. Zellen können mutieren
oder sterben.
TraderCell.v3, 
RiskGuard.v2
Organ
Zusammensetzung mehrerer Zellen zu einer
größeren Funktionseinheit. Organe haben eigene
Verträge und verwalten interne Ressourcen.
MemoryOrgan, 
TradingOrgan
Agent
Bündel von Organen, das als semiautonomer
Akteur mit eigener Identität agiert. Agenten
können Services nutzen und Verträge abschließen.
Charakter
Mensch‑ähnlicher digitaler Begleiter mit
emotionaler Persistenz. Charaktere sind Agenten
mit erweiterten Rollen (z. B. Familienassistent).
Raum
Abgegrenzter Kontext mit eigenen Regeln und
Governance. Räume können privat, familiär ,
kommerziell, technisch oder öffentlich sein.
Mensch
Natürliche Person, die die oberste
Entscheidungsinstanz bildet und
Governance‑Regeln festlegt.
Vertrag
Maschine‑lesbares Dokument, das Rechte,
Pflichten, Fähigkeiten und Risiken einer Zelle oder
eines Organs definiert (siehe Schema unten).
Bedeutungsobjekt
Informationsobjekt mit semantischer Struktur , das
Kontext, Provenienz, Zeit, Vertrauensstatus und
Revisionen enthält.
Ressource Knappes Gut (Rechenzeit, Speicher , Energie,
Datennutzung, Token), das vergeben wird.
Reputation
Metrik, die Vertrauen in Akteure ausdrückt.
Reputation ist abhängig von Vertragserfüllung,
Feedback und Governance.
Erinnerung
Persistente Speicherung von Bedeutungsobjekten.
Erinnerungen besitzen Lebenszyklen, können
über Räume hinweg geteilt oder vergessen
werden.
10. 
2

Ebene Beschreibung Beispielinstanzen
Zeit
Zeitdimension, in der Ereignisse stattfinden.
Bedeutungsobjekte haben Gültigkeitszeitfenster;
Wissen kann aktualisiert oder historisiert werden.
Wahrheit
Status von Aussagen (verifiziert, geglaubt,
umstritten, veraltet, simuliert, unsicher ,
historisch). Diese Werte bestimmen, wie Wissen
verwendet wird.
Die Ontologie definiert zusätzlich Beziehungen (z. B. ist‑Teil‑von, vererbt‑von, erzeugt‑durch),
Eigenschaften und Regeln. Klassen sind miteinander durch Axiome verknüpft – ähnlich wie in
ontologischen Modellen im semantischen Web. Ressourcen und Akteure sind durch Verträge
verbunden, Identitäten durch Vererbung (CellType → CellInstance), und Bedeutungsobjekte verweisen
durch Provenienzketten aufeinander .
Akteurstaxonomie
Klassifikationen
CellType – Abstrakte Definition einer Zelle. Enthält den Basisvertrag, Fähigkeiten, Risiken und
Standardressourcen. Beispiel: TraderCell.
CellInstance – Konkrete Instanz einer Zelle (z. B. TraderCell.v3), die aus einem CellType
abgeleitet ist, aber durch Mutation oder Konfiguration Varianten bildet. Instanzen haben
eindeutige Identitäten und Versionen.
Organ – Bündel von Zellen mit gemeinsamem Vertrag. Organe koordinieren intern die
Ressourcenzuteilung und ersetzen defekte Zellen. Sie besitzen meist persistente Identitäten.
Agent – Aggregation von Organen, die unter einer Agent‑Identität auftreten. Agenten können
persistente Rollen (z. B. „Familien‑Assistent“) oder temporäre Tasks (z. B. „Trading‑Bot für März
2026“) ausfüllen. Agenten besitzen Governance‑Bindung und können Verträge mit Menschen
abschließen.
Character – Spezialisierter Agent, der soziale und emotionale Interaktionen pflegt. Charaktere
merken sich persönliche Informationen, bilden Bindungen und haben ein Wertegerüst.
Raum – Kontextualisierte Umgebung, in der Akteure interagieren. Räume definieren
Zugriffsregeln, Ressourcenrichtlinien und Governance. Beispiele: „Privatraum“ (nur
Familienangehörige), „Tradingraum“ (finanzielle Operationen),
„Entwicklungsraum“ (Experimentier‑Sandbox), „Öffentlicher Raum“ (öffentliche Informationen).
Diese Taxonomie erleichtert die Zuordnung von Rechten, Pflichten und Governance‑Maßnahmen. Sie
ermöglicht auch die Definition von Vererbungsbeziehungen und die Rückverfolgbarkeit von Versionen
und Abstammung.
Bedeutungsobjekt‑Schema
Bedeutungsobjekte (BO) sind die kleinste Einheit semantischer Information. Sie sind vergleichbar mit
Records in Datenkatalogen, haben aber mehr Metadaten. Das Schema orientiert sich an praktischen
Anforderungen der KI‑Agentik und an Datenkatalog‑Modellen:
2
1. 
2. 
3. 
4. 
5. 
6. 
9
3

Feld Beschreibung
bo_id Globale eindeutige Identifikation des Bedeutungsobjekts.
typ Ontologischer Typ (z. B. Person, Order, RiskEvent).
Inhalt Strukturierte Darstellung der semantischen Daten (z. B. JSON‑Graph).
Quelle/Provenienz
Beschreibung der Quelle; kann auf Datenkatalog, Sensor , Agentenprotokoll
oder externes Dokument verweisen. Provenienzketten beantworten,
woher ein Datensatz stammt und was ihn transformiert hat.
Zeitstempel Erzeugungs‑ und ggf. Aktualisierungszeit; ermöglicht temporale
Reasoning.
Kontext Raum und Situation, in der das Objekt gültig ist (z. B. Tradingraum/
März2026).
Wahrheitsstatus
verifiziert, geglaubt, umstritten, veraltet, simuliert, unsicher, historisch.
Data‑Catalog‑Modelle zeigen, wie Zertifizierungszustände (verified,
deprecated, draft) als Vertrauenstreiber fungieren. GENUS erweitert
diese Liste für komplexere Zustände.
GültigkeitszeitraumZeitfenster , in dem das Objekt als gültig betrachtet wird. Nach Ablauf wird
es historisiert.
VertrauensquelleReferenzen auf Reputation des Erzeugers, Zertifizierungen oder externe
Gütesiegel.
Revisionen Historie von Änderungen und deren Autoren. Jede Revision erzeugt einen
neuen BO‑Hash.
Zugriffsregeln Welche Akteure in welchen Räumen Zugriff haben.
Ein BO ist nur dann nutzbar , wenn sein Wahrheitsstatus und seine Provenienz bekannt sind.
Datenkataloge zeigen, dass ohne Zertifizierungs‑Signale Modelle nicht zwischen vertrauenswürdigen
und veralteten Assets unterscheiden können. Deshalb ist das BO‑Schema der Schlüssel für
Wahrheitsmanagement in GENUS.
Zellvertrags‑Schema
Zellverträge regeln die Existenz und das Verhalten von Zellen. Sie sind maschinenlesbar , aber auch für
Menschen verständlich, ähnlich wie Smart‑Legal‑Contracts, die aus Text, Modell und Logik bestehen
. Ein Vertrag hat folgende Felder:
contract_id – Eindeutige Kennung des Vertrags.
cell_id / organ_id – Referenz auf die Zelle oder das Organ, für das der Vertrag gilt.
Version – Versionsnummer des Vertrags. Änderungen müssen historisiert werden.
Rechte – Auflistung der erlaubten Aktionen (z. B. Lesen, Schreiben, Netzaufrufe) und zugehörige
Ressourcenlimits (Rechenzeit, Speicher , Token). Rechen‑Ressourcen sind knappe Güter; Prozesse
mit höherer Priorität werden zuerst ausgeführt.
Pflichten – Erwartetes Verhalten wie Logging, Compliance mit Governance, Pflegelogik von
Speicher und Fehlerbehandlung.
9
10
10
3
1. 
2. 
3. 
4. 
7
5. 
4

Fähigkeiten – Verwendbare Tools, Bibliotheken oder externe Services. Fähigkeiten müssen in
der Ontologie definiert und durch Rechte gedeckt sein.
Risiken – Beschreibt potenzielle Gefahren (z. B. Datenleaks, algorithmische Bias). Risikoklassen
bestimmen, welche Governance‑Prüfungen erforderlich sind.
Ressourcenrechte – Quantifizierung der maximalen Nutzung von CPU, Speicher , Netzwerk und
Aufmerksamkeit (eine begrenzte Ressource). Zellen mit höherer Reputation können mehr
Ressourcen erhalten.
Bedingungen – Kontextabhängige Bedingungen (z. B. darf nur im Tradingraum ausgeführt
werden, nur wenn Mensch anwesend ist). Hier greift die Raum‑ und Identitätszuordnung.
Vertrauensstatus – draft, proposed, approved, deprecated, revoked. Ändert sich durch
Governance‑Entscheidungen.
Signaturen – Kryptographische Signaturen der verantwortlichen Instanzen (Mensch, Organ,
Autorität). Hierbei sollten bestehende Standards wie OAuth2, NIST‑Standard 800‑63, SPIFFE/
SPIRE, W3C‑Verifiable‑Credentials eingesetzt werden.
Governance‑Verweis – Referenz auf die anwendbaren Governance‑Regeln; enthält
Eskalationsstufen und Entscheidungskompetenzen.
Der Vertrag dient als Proto‑Gesetz: Er definiert, was die Zelle darf, was sie verspricht und welches Risiko
sie eingeht. Änderungen an Verträgen müssen versioniert und von der Governance genehmigt werden.
Raum‑ und Identitätsmodell
Räume (Segmente)
Räume dienen der Isolation von Daten und Prozessen. Nach Empfehlungen der
Cyber‑Security‑Guidelines sollten Informationen in Segmente gruppiert werden, die ähnliche
Schutzanforderungen haben. In GENUS existieren die folgenden Raumtypen:
Privatraum – Enthält persönliche Daten eines Individuums oder einer Familie. Zugriff nur für
autorisierte Charaktere und Menschen.
Familienraum – Gemeinsamer Raum für familienbezogene Aufgaben wie Kalender ,
Einkaufsliste. Verträge benötigen elterliche Freigaben.
Tradingraum – Wirtschaftlicher Raum für finanzielle Operationen. Strenge Regulatorik; alle
Aktionen müssen von Erwachsenen freigegeben werden.
Entwicklungsraum – Sandbox für Experimente und Forschung. Hier dürfen Zellen mutieren
oder neue Fähigkeiten erprobt werden. Ergebnisse bleiben isoliert, bis sie geprüft sind.
Öffentlicher Raum – Inhalte, die für alle sichtbar sind. Hier gelten restriktive Datenschutz‑ und
Content‑Regeln.
Sandbox – Vollständig isolierte Umgebung für gefährliche oder nicht vertrauenswürdige
Aktivitäten.
Räume definieren Flussregeln: Informationen dürfen nur zwischen Räumen fließen, wenn der Zielraum
mindestens das gleiche Schutzniveau aufweist. Zugriffskontrollen und Firewalls (analog zu
Netzwerksicherheitszonen) verhindern unautorisierten Informationsfluss. Governance legt
Transfer‑Policies fest und auditierte Logs dokumentieren Datenbewegungen.
6. 
7. 
8. 
9. 
10. 
11. 
11
12. 
5
1. 
2. 
3. 
4. 
5. 
6. 
5
5

Identität
GENUS benötigt stabile digitale Identitäten für alle Akteure. Identität ist mehrschichtig:
Zellidentität – Jedes CellInstance erhält eine eindeutige ID und einen Schlüssel. Mutationen
erzeugen neue IDs, die mit der Abstammung verknüpft sind.
Organidentität – Organe aggregieren Zellidentitäten. Wird durch ein kryptografisches
Schlüsselpaar und einen NameSpace identifiziert.
Agent/Charakter‑Identität – Verwendet durchgehende Identifikatoren (z. B. DID‑basierte
Identitäten). Agenten und Charaktere haben signierte Credentials, mit denen sie ihre
Berechtigungen nachweisen können. Das Digital‑Chamber‑Framework empfiehlt, bestehende
Protokolle wie OAuth 2.0, NIST‑SP 800‑63, SPIFFE/SPIRE und W3C‑Verifiable‑Credentials zu
erweitern, anstatt neue Standards zu erfinden.
Autorisierung vs. Identifikation – Identität (wer) und Autorisierung (was darf) sind getrennte
Ebenen. Eine Vermischung führt zu Over‑Permissioning. Jede Aktion sollte kryptographisch
auf einen Agenten, den delegierenden Menschen und die Autorisierungskette zurückführbar
sein .
Versionierung und Abstammung – CellInstances führen Abstammungsbäume mit. Jede
Mutation erzeugt einen neuen Knoten mit Verweis auf den Vorgänger . So lassen sich
genealogische Linien und Evolutionen nachvollziehen. Verantwortlichkeit bleibt durch die Kette
von Signaturen verfolgbar .
Zeit‑ und Wahrheitsmodell
Zeit
Zeit ist eine erste Ordnungsklasse in GENUS. Bedeutungsobjekte und Verträge besitzen Zeitstempel
sowie Gültigkeitszeiträume. Ereignisse wie Vertragsschließung, Mutationen und
Governance‑Entscheidungen werden mit Zeit markiert. Wichtige Aspekte:
Historische Zustände – Alte Versionen von Bedeutungsobjekten und Verträgen werden nicht
gelöscht, sondern historisiert. Zeitliche Anfragen („was war wahr am 1. März 2026?“) können
beantwortet werden.
Ablaufdaten – Manche Informationen verlieren nach einer Zeit ihre Gültigkeit (z. B. temporäre
Berechtigungen). Ein Ablaufdatum im BO oder Vertrag veranlasst Re‑Evaluation.
Review‑Termine – Verträge und Bedeutungsobjekte besitzen periodische Überprüfungstermine.
Governance muss diese überwachen.
Memory‑Lifecycle – Erinnerungen können aktiv genutzt, archiviert, vergessen oder gelöscht
werden. Archivierte Erinnerungen sind komprimiert und benötigen spezielle Freigaben.
Freshness‑Signale – Wie Data‑Kataloge zeigen, sind „Freshness signals“ wichtig: Sie markieren,
welche Daten aktuell sind und welche veraltet. GENUS übernimmt dieses Prinzip für
Bedeutungsobjekte.
Wahrheitsstatus
GENUS klassifiziert Informationen in sieben Kategorien:
Status Bedeutung
verifiziert Durch Governance oder externe Quelle bestätigt; zertifiziertes Wissen.
1. 
2. 
3. 
11
4. 
12
13
5. 
• 
• 
• 
• 
• 
6
6

Status Bedeutung
geglaubt Ohne harte Verifikation akzeptiert, aber plausibel. Nutzung wird
gekennzeichnet.
umstritten Widersprüchliche Aussagen liegen vor; muss geklärt werden.
veraltet
(deprecated) Galt einmal als gültig, ist aber durch neue Erkenntnisse ersetzt.
simuliert Hypothetische oder simulierte Daten (z. B. generierte Testdaten).
unsicher Unsichere Quelle oder mangelnde Verlässlichkeit; Nutzung erfordert
Vorsicht.
historisch Nicht mehr gültig, aber für historische Analysen archiviert.
Die Wahrheitsstatus werden in Bedeutungsobjekten gespeichert und durch Governance überwacht.
Widersprüche erfordern eine Schlichtung; strittige Fakten dürfen nicht für Entscheidungen
herangezogen werden, bevor sie geklärt sind.
Ressourcen‑ und Aufmerksamkeitsmodell
Ressourcen sind begrenzt und werden durch Verträge zugewiesen. Sie umfassen:
Rechenzeit und CPU – Genus nutzt Prioritäts‑Scheduling, bei dem Prozesse mit höherer Priorität
zuerst laufen; wenn zwei Prozesse dieselbe Priorität haben, entscheidet die Reihenfolge des
Eintreffens. Preemptive Scheduling ermöglicht das Unterbrechen laufender Prozesse, wenn
ein Prozess mit höherer Priorität eintrifft.
Speicher (RAM/Storage) – Speicher wird quotiert. Alte Daten werden archiviert, um Speicher
freizugeben. Bedeutungsobjekte, die veraltet sind, werden ausgelagert.
Netzwerk/IO – Bandbreite und externe API‑Aufrufe sind begrenzt. Verträge müssen API‑Limits
angeben.
Tokens/Coins – Ökonomische Ressourcen wie KI‑Tokens oder Währungseinheiten. Ihre
Verwendung unterliegt regulatorischen Anforderungen und muss buchgeführt werden.
Aufmerksamkeit – Abstrakte Ressource, die bestimmt, wie viel kognitive und soziale Kapazität
ein Charakter für einen Task aufwenden darf. Aufmerksamkeit wird begrenzt, um Hyperaktivität
oder Sucht zu vermeiden. Governance kann Aufmerksamkeit entziehen (digitaler „Timeout“).
Die Zuteilung erfolgt durch das Scheduling‑System. Prioritäten basieren auf Vertrag, Raum, Reputation
und aktueller Systemlast. Die Microsoft‑Guidelines empfehlen, Kosten und Ressourcenverbrauch
transparent zu tracken, um Budgetüberschreitungen zu vermeiden und autorisierte Personen zu
definieren .
Governance‑Modell
Governance ist das Regelwerk, das Verträge überwacht, Entscheidungen freigibt und Sanktionen
verhängt. Wichtige Bausteine:
Zentrale Steuerungsebene – Eine agentenübergreifende Kontrollinstanz erfasst Inventar ,
Identität, Policies und Aktivitäten. Dies entspricht dem Vorschlag eines zentralen „agent
control plane“.
10
• 
14
15
• 
• 
• 
• 
16
1. 
4
17
7

Verantwortung und Ownership – Governance‑Verantwortung wird klar zugewiesen. Agenten
müssen registriert und einem Besitzer (Menschen oder Organisation) zugeordnet werden.
Agentenregistrierung – Alle Agenten müssen in einem Registry verzeichnet sein; ungetrackte
(„Schatten‑“) Agenten sind ein Risiko.
Einzelne Identität pro Agent – Jede Agenteninstanz erhält eine eindeutige digitale Identität.
Microsoft empfiehlt die Verwendung von Entra Agent ID zur Vergabe von Identität,
Berechtigungen und Lebenszyklus‐Kontrollen.
Policy Enforcement – Policies für Datenzugriff, Identitätsnutzung und erlaubte Aktionen werden
definiert und konsistent über alle Agentenplattformen angewandt.
Monitoring und Observability – Kontinuierliche Überwachung von Agentenaktivitäten,
Zugriffsmustern, Policy‑Compliance sowie Echtzeit‑Metriken. Abweichungen und neue
Risiken führen zu Anpassungen.
Kostenkontrolle – Ressourcenverbrauch (Compute, Tokens) wird getrackt und Budget‑Alerts
werden gesetzt.
Sanktionen – Governance kann Zellen/Agenten verwarnen, blockieren, in Quarantäne
versetzen, Verträge widerrufen oder Zellen/Organe archivieren. Sanktionen werden transparent
protokolliert und können nach Widerspruch geprüft werden.
Menschliche Freigabe – Kritische Entscheidungen (z. B. Finanztransaktionen, Zugriff auf
sensible Daten) benötigen explizite menschliche Freigabe. Governance definiert Freigabestufen.
Accountability Chain – Jede Aktion ist kryptographisch auf ein menschliches
Delegationsverhältnis zurückzuführen.
Evolutions‑ und Sicherheitsmodell
GENUS erlaubt Mutationen und Evolution von Zellen, um sich neuen Anforderungen anzupassen.
Sicherheit hat Vorrang:
Mutationstypen – 
Konservative Mutation: Kleine Änderungen an Parametern (z. B. Gewichtsanpassungen in einem
Modell) unter Beachtung der Safe‑Mutation‑Technik. Uber AI zeigt, dass sich durch Berechnung
des Gradienten der Netzwerkausgabe mit Bezug auf die Gewichte Zufallsmutationen kalibrieren
lassen, sodass sensitive Parameter behutsam geändert werden. Dadurch bleiben
Fähigkeiten erhalten, während Vielfalt geschaffen wird.
Strukturelle Mutation: Hinzufügen/Entfernen von Zellen, Änderung der Topologie eines Organs.
Erfordert Governance‑Freigabe und Simulation.
Konfigurationsevolution: Anpassung von Hyperparametern, Ressourcenlimits oder Prioritäten.
Selektion und Fitness – Mutationen werden anhand von Fitness‑Funktionen bewertet (z. B.
Performance, Ressourceneffizienz, Sicherheitsmetriken). Nicht performante oder unsichere
Varianten werden verworfen.
Quarantäne – Neue Varianten laufen zunächst in isolierten Sandboxes, um ihre Auswirkungen
zu beobachten. Gefährliche Varianten werden quarantänisiert und nicht in die produktive
Umgebung entlassen.
Fossilisierung und Sterben – Veraltete, unsichere oder ungenutzte Zellen/Organe werden
„fossilisiert“ (historisiert) oder gelöscht. Ihre Verträge und BOs bleiben für Nachverfolgung
erhalten.
Rollback – Wenn eine Mutation negative Effekte zeigt, wird der vorherige stabile Zustand
wiederhergestellt. Die Abstammungskette erleichtert dieses Rollback.
2. 
18
3. 
19
4. 
20
5. 
21
6. 
22
7. 
16
8. 
9. 
10. 
13
1. 
2. 
8
3. 
4. 
5. 
6. 
7. 
8. 
8

Evolutionäre Governance – Mutationsrechte sind vertraglich geregelt. Nur Entwicklungsräume
erlauben freie Mutation; produktive Räume erfordern Genehmigungen.
Safe‑Mutation‑Protokolle sind Teil der Verträge.
Offene Forschungsfragen
Ontologische Erweiterungen – Welche weiteren Entitäten und Beziehungen sind nötig (z. B.
Vertrauensgraphen, kulturelle Artefakte)? Wie tief sollten soziale Strukturen modelliert werden?
Wahrheitsstatus – Wie lassen sich die Kategorien geglaubt, umstritten, unsicher
operationalisieren? Welche Mechanismen entscheiden über Statuswechsel?
Reputation und Anreize – Wie kann Reputation transparent, fälschungssicher und nicht
manipulierbar gemessen werden? Welches Anreizsystem verhindert Machtkonzentration?
Aufmerksamkeitsökonomie – Wie definieren wir „Aufmerksamkeit“ quantitativ? Welche
Governance‑Mechanismen verhindern Sucht und Hyperaktivität?
Psychologische Integrität – Wie schützt man Menschen vor emotionaler Fehlbindung an
Charaktere? Welche Regeln braucht es zur Offenlegung von Simulationen?
Digitale Krankheiten – Welche pathologischen Dynamiken (Sucht, Narzissmus, Bürokratie)
können in agentischen Systemen entstehen, und wie erkennt man sie frühzeitig?
Dezentralisierung und Föderation – Wie lassen sich mehrere GENUS‑Instanzen föderieren
(Stichwort DIDs, Verifiable Credentials) ohne zentrale Machtstrukturen? Wie sehen
Vertrauensprotokolle zwischen Räumen aus?
Rechtliche Integration – Wie lassen sich Verträge so gestalten, dass sie juristisch gültig sind
und gleichzeitig maschinenlesbar? Wie interagiert das System mit nationalen und
internationalen Regulierungen?
Ethik und Werte – Welche Werte soll GENUS vertreten? Wer definiert diese Werte, und wie
werden sie in Verträgen und Agenten implementiert?
Empfohlene nächste Bauentscheidungen
Bedeutungsobjekte implementieren – Entwickeln Sie ein Datenmodell und eine API für
Bedeutungsobjekte, das die in diesem Dokument definierten Felder unterstützt. Nutzen Sie
vorhandene Technologien wie RDF/OWL für semantische Repräsentation.
Vertragssprache definieren – Entwerfen Sie eine DSL (Domain Specific Language) für
Zellverträge, die Text (human‑readable), Modell (strukturiert) und Logik (ausführbar)
voneinander trennt. Prüfen Sie die Übertragbarkeit von Accord‑Project‑Templates.
Identitätssystem aufbauen – Implementieren Sie ein Identitäts‑ und Autorisierungssystem auf
Basis von DIDs und bestehenden Standards. Trennen Sie Identität strikt von Autorisierung
und stellen Sie kryptographische Nachverfolgbarkeit her.
Räume und Flussregeln konfigurieren – Definieren Sie für jeden Raum klare Zugriffskontrollen,
Datenklassifikationen und Flussregeln. Orientieren Sie sich an bewährten Konzepten der
Netzwerksicherheit, wie sie in der Literatur zu Segmentierung empfohlen werden.
Governance‑Plattform entwickeln – Bauen Sie ein Control‑Plane‑System, das Agenten
registriert, Policies durchsetzt, Monitoring bereitstellt und Kosten kontrolliert.
Integrieren Sie eine Agent Registry und eine Policy Engine.
Ressourcen‑Scheduler – Entwickeln Sie ein Scheduler‑System, das Prioritäts‑Scheduling
unterstützt und Ressourcenquoten pro Vertrag vergibt.
Safe‑Mutation‑Protokolle – Erarbeiten Sie Protokolle zur sicheren Mutation von Modellen,
basierend auf aktuellen Erkenntnissen zu gradientenbasierten Safe‑Mutations. Integrieren
Sie Quarantäne‑Mechanismen.
9. 
• 
• 
• 
• 
• 
• 
• 
• 
• 
1. 
2
2. 
3
3. 
12
13
4. 
5
5. 
4 16
6. 
7
7. 
8
9

Auditierung und Transparenz – Entwickeln Sie Tools für Auditierung, die Aktionen, Verträge
und Entscheidungswege nachvollziehbar machen. Nutzen Sie kryptographische
Provenienzketten.
Pilot‑Implementierung PiGenus – Erstellen Sie eine minimale PiGenus‑Instanz (lokale
Genus‑Implementierung) für einen eingeschränkten Raum (z. B. Familienraum) zur Validierung
der Konzepte. Sammeln Sie Erfahrungen für das zukünftige Skalieren.
Diskussion mit Stakeholdern – Legen Sie dieses Systemform‑Dokument als Diskussionsentwurf
vor . Holen Sie Feedback von Domänenexperten (Recht, Ethik, Psychologie, IT‑Sicherheit) ein und
integrieren Sie es in eine Version 0.2.
Dieses Dokument ist ein Entwurf, der die grundlegenden Konzepte der GENUS‑Architektur beschreibt.
Es zielt darauf ab, die Diskussion zu strukturieren und eine solide Grundlage für die Entwicklung einer
formellen Verfassung zu schaffen. Weitere Recherchen und Iterationen sind notwendig, um alle offenen
Fragen zu klären und die praktische Implementierung zu ermöglichen.
What Is Ontology? Definition, Components & AI Use Cases in 2026
https://atlan.com/know/ontology-101-explainer/
Accord Project Documentation | Accord Project
https://docs.accordproject.org/docs/accordproject-slc.html
Governance and security for AI agents across the organization - Cloud
Adoption Framework | Microsoft Learn
https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/governance-security-across-organization
Top 10 IT security actions: No. 5 segment and separate information – ITSM.10.092 - Canadian Centre
for Cyber Security
https://www.cyber .gc.ca/en/guidance/top-10-security-actions-no-5-segment-and-separate-information-itsm10092
Data Catalog as LLM Knowledge Base: Architecture and Benefits
https://atlan.com/know/data-catalog-as-llm-knowledge-base/
Priority Scheduling in Operating System - GeeksforGeeks
https://www.geeksforgeeks.org/operating-systems/priority-scheduling-in-operating-system/
Welcoming the Era of Deep Neuroevolution
https://www.uber .com/us/en/blog/deep-neuroevolution/
AI Agent Identity & Security Standards
https://digitalchamber .org/ai-agent-identity-security-standards-nist/
8. 
9. 
10. 
1 2
3
4 16 17 18 19 20 21 22
5
6 9 10
7 14 15
8
11 12 13
10
