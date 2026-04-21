# JEFF a evaluator-centered self-improving agent systems

## Výkonný souhrn

JEFF už dnes podle svého repozitáře stojí na správném základu pro jakýkoli pozdější pokus o omezené self-improvement: staví se jako CLI-first persisted runtime, zdůrazňuje truthful inspection, bounded `/run`, approval-gated continuation a anti-drift coverage, a současně se výslovně neprodává jako skrytě autonomní systém nebo široký „memory product“. To je mnohem zdravější výchozí pozice než u většiny agent paperů, které začínají u „dělej víc smyček“ a governance řeší až zpětně. citeturn40view0

Hlavní závěr je tvrdý a jednoduchý: skutečně důvěryhodné self-improving systémy dnes skoro nikdy nevypadají jako velká rekurzivní sci-fi. V praxi fungují hlavně dvě věci. První je **silně evaluator-centered bounded adaptation**: explicitní metrika, train/val oddělení, rozpočtový limit, návrat jen nejlepší varianty na full validation. To dnes nejlépe reprezentují **DSPy MIPROv2** a **DSPy GEPA**. Druhá je **patch-and-benchmark self-modification** v izolovaném sandboxu: agent upraví svůj scaffold nebo kód, spustí benchmark nebo test harness a teprve pak se někdo rozhodne, zda změna přežije. To reprezentují **SICA**, **Darwin Gödel Machine** a **Huxley-Gödel Machine**. Všechno ostatní je buď užitečný lokální repair trick, nebo čisté divadlo. citeturn25view2turn25view1turn24view0turn33view3turn37view0turn7view7turn40view2

Nejsilnější praktické systémy pro JEFF nejsou ty, které o sobě křičí „recursive self-improvement“, ale ty, které mají **explicitní externího soudce** a umí **selhat uzavřeně**. MIPROv2 optimalizuje instrukce i few-shot demonstrace proti zadané metrice, používá validační sadu, minibatch evaluaci a pravidelné full-validation checkpointy a vrací konfiguraci, která byla nejlepší na plném validačním běhu. GEPA jde dál: bere trace programu, umí z metriky přijmout i slovní feedback, pracuje s Pareto frontou a její dokumentace výslovně varuje, že bez odděleného valsetu prompt optimizer prompty prostě přeučí na trainset. To je přesně ten typ explicitní disciplíny, který JEFF potřebuje. citeturn25view2turn25view1turn25view0turn24view0turn33view3turn33view4turn33view5

Naopak nejvíc sexy systémy v prostoru self-modifying coding agents jsou zatím pořád prototypy. **SICA** je legitimní výzkum, protože opravdu nechává agenta editovat vlastní codebase, použije benchmarky, archivuje výsledky a dokonce hodnotí utility přes výkon, čas a cenu. **DGM** je legitimní výzkum, protože skutečně generuje patche vlastního scaffoldingu, běží je přes benchmark harness a archivuje potomky. **HGM** je legitimní výzkum, protože správně útočí na reálný problém DGM-style smyček: současný benchmark score není totéž co budoucí self-improvement potential. Jenže ani jeden z těchto systémů zatím není hotový pro trust-sensitive architekturu: SICA ukazuje výsledek na náhodném podvzorku SWE-Bench Verified; DGM přímo načítá SWE-Bench Verified a jeho archivní politika je ve výchozím nastavení příliš benevolentní; HGM sice zlepšuje search criterion, ale pořád dědí veřejné benchmarky a tutéž základní eval ekonomiku. citeturn37view0turn38view0turn38view4turn39view0turn7view7turn18view0turn19view0turn40view2turn41view0

Největší lži v tomto prostoru se opakují pořád dokola. První lež: **retry loop není self-improvement**. Self-Refine je explicitně jedna a tatáž LLM v roli generátoru, feedback providera i refinera; Reflexion sice umí využít externí feedback, ale sama práce s pamětí reflexí ještě není důkaz robustní dlouhodobé adaptace; a silná kritika intrinsic self-correction ukazuje, že bez externího feedbacku reasoning často nekorigujete, ale zhoršíte. Druhá lež: **leaderboard gain není totéž co robustní schopnost**. U SWE-Bench Verified je problém už veřejný: entity["company","OpenAI","ai company"] zveřejnilo audit, podle nějž benchmark trpí jak flawed tests rejecting correct solutions, tak kontaminací, a proto už ho nedoporučuje jako frontier capability measure; komunita mezitím tlačí k privátnějším a decontaminated evalům jako SWE-Bench Pro a SWE-rebench. citeturn32view3turn32view0turn32view4turn32view5turn6view12turn35search20turn6view14

Nejtvrdší praktická lekce je tahle: **evaluator-centered self-improvement je pro produkční architekturu použitelný už dnes, ale jen v bounded podobě**. Je připravený pro prompt optimization, routing optimization, workflow search a izolované patch-laby s deterministickými regresními testy, holdout evaly, budget guardrails a lidským schválením. Není připravený pro tiché autonomní přepisování trust core, governance vrstvy, pravdivostního modelu stavu ani approval mechanismu. Pokud JEFF zkusí víc než tohle, bude si koledovat o benchmarkové divadlo, ne o skutečné zlepšování. citeturn40view0turn25view2turn24view0turn38view0turn6view12

## Taxonomie evaluator-centered self-improvement smyček

### Pravé benchmark-driven self-improvement smyčky

Tohle je nejtvrdší a zároveň nejrizikovější třída. Agent nebo scaffold mění **svůj vlastní kód**, pak se na něj pustí benchmark/test harness a změna se archivuje, případně dál rozvíjí. Do této třídy patří **SICA**, **Darwin Gödel Machine** a **Huxley-Gödel Machine**. U SICA je smyčka doslova „vyhodnoť aktuálního agenta → ulož do archivu → pusť ho na jeho vlastní codebase → vyhodnoť znovu“, přičemž paper výslovně definuje utility přes benchmark score, čas i cenu. DGM a HGM dělají totéž v evolučním stylu, s archivem variant a benchmarky SWE-bench/Polyglot jako externím soudcem. Tahle třída je skutečná. Tohle není marketing. Ale je pořád křehká, protože kvalita celé smyčky je brutálně závislá na kvalitě benchmarku a regression discipline. citeturn39view0turn38view0turn38view1turn7view7turn18view0turn19view0turn40view2turn41view0

### Evaluator-guided bounded adaptation

Tohle je dnes nejzdravější a pro JEFF nejrelevantnější třída. Nemění se celý agent bezhlavě; mění se **prompty, instrukce, few-shot příklady, workflow struktura nebo textové komponenty** a každá kandidátní změna je tlačena přes explicitní metriku na train/val nebo val/test splitu. Sem patří **MIPROv2**, **GEPA**, **OPRO**, **Promptbreeder**, částečně **AFlow** a **ADAS**. MIPROv2 a GEPA jsou nejdisciplinovanější: budget caps, validační sada, hledání nejlepší konfigurace, návrat jen vítěze. OPRO a Promptbreeder jsou užší a historicky důležité, ale méně provozně disciplinované. AFlow a ADAS jdou od promptů k celým workflow architekturám, což je zajímavější, ale také mnohem náchylnější k benchmark overfittingu a reprodukčním bolestem. citeturn25view2turn25view1turn24view0turn24view3turn31view1turn31view0turn16view6turn21view0turn16view2turn20view0

### Patch-and-test repair loops

Tohle nejsou persistent self-improving systémy, ale jsou důležité jako **kontrolní skupina reality**. **SWE-agent** a **mini-SWE-agent** ukazují, že externí pass/fail harness, kvalitní agent-computer interface a repo-level tools často přinesou víc než metafyzika kolem „reflexe“. **CRITIC** a **Self-Debugging** jsou také užitečné, protože využívají externí nástroje nebo execution results k opravě výstupu. Jenže to obvykle zlepšuje **jednotlivý běh nebo konkrétní výstup**, ne trvale agentovu politiku. Tohle je důležité rozlišit: opravdu užitečné repair loop ano, ale persistent self-improvement ne. citeturn27search0turn27search8turn32view6turn32view7turn32view9

### Experience-memory adaptation

Sem patří systémy jako **ExpeL**, které sbírají zkušenosti z training tasks, extrahují z nich inspectable natural-language insights a pak tyto insighty používají při inference na dalších úlohách. To je blíž tomu, co JEFF nazývá „memory as non-truth continuity“: zkušenost pomáhá, ale sama o sobě není pravda. ExpeL je relevantní právě proto, že se neopírá o halucinované „už jsem chytřejší“, ale o zážitky z prostředí a následnou extrakci pravidel. Slabina je jasná: evaluátor je environment success, ne robustní regression suite pro změnu architektury, a proto to není dobrý model pro úpravy trust core. citeturn28view0turn29view0turn29view4turn29view7

### Reflection-only loops a benchmarkové divadlo

Tady je potřeba být nemilosrdný. **Self-Refine** je užitečný inference trick, ale není to bezpečný self-improvement framework. Ten samý model generuje, kritizuje i opravuje. To je uzavřený kruh bez soudce. **Reflexion** je lepší, pokud dostává skutečný externí task feedback, ale v okamžiku, kdy se z něj dělá obecná filozofie „language agent se zlepšuje reflexí“, sklouzává to k rétorice. A kritická práce o intrinsic self-correction ukazuje přesně proč: bez externího feedbacku se reasoning často nezlepší a někdy se dokonce zhorší. Pokud loop nedokáže robustně vyznačit **regression**, **inconclusive result** nebo **hard reject**, není to self-improvement. Je to self-justification engine. citeturn32view3turn32view0turn32view1turn32view4turn32view5

## Kompaktní srovnávací tabulka

Legenda skóre: **EV/AR/AU/BO/RG/RW/RP/RJ** = evaluator strength / anti-regression / auditability / boundedness / resistance to benchmark gaming / real-world usefulness / reproducibility / architectural relevance to JEFF. Skóry jsou moje hodnoticí inference nad primárními zdroji, ne claim autorů. Tam, kde je důkaz slabý, je skóre úmyslně přísné. 

### Seriózní kandidáti

| Systém | Typ | Co se zlepšuje | Evaluátor | Přijetí a anti-regrese | Silné stránky | Slabiny | Zralost / použitelnost | Relevance pro JEFF | Skóre | Zdroje |
|---|---|---|---|---|---|---|---|---|---|---|
| Huxley-Gödel Machine | pravá self-modifikace / coding / open | kód agenta + search policy nad stromem self-modifikací | SWE-bench Verified + Polyglot, ale rodiče vybírá přes odhad clade promise CMP | lepší search discipline než score-only; anti-regrese stále benchmark-centric | správně rozlišuje current score vs. future self-improvement potential | stále veřejné benchmarky; „human-level“ claim je benchmark-proxy, ne důkaz obecné spolehlivosti | slibný výzkum, dnes jen částečně použitelný | velmi vysoká | 4/4/4/4/2/3/4/5 | citeturn40view2turn41view0 |
| Darwin Gödel Machine | pravá self-modifikace / coding / open | vlastní scaffold, tools, prompty, long-context handling, peer-review, file ops | SWE-bench Verified + Polyglot harness | compile filter; small/medium/big subset eval; default archiv může držet všechny zkompilované děti | explicitní archive, metadata, sandboxing, reálná self-edit smyčka | používá Verified přímo; default `keep_all`; přeučení na veřejný benchmark je reálné riziko | slibný výzkum, částečně použitelný v labu | velmi vysoká | 4/3/4/3/2/2/4/5 | citeturn7view7turn18view0turn19view0turn9view7turn6view12 |
| SICA | pravá self-modifikace / coding / open | celá codebase agenta, včetně promptů/scaffoldu | benchmark utility přes výkon, čas a cenu; benchmark suite v archivu | best agent from archive se stává meta-agentem; detailní benchmark logs a meta_improvement logs | audit trail, utility místo čistého leaderboardu, overseer, dobrá JEFF-kompatibilní archivace | jen random subset SWE-Bench Verified; repo samo přiznává variance a potřebu realističtějších benchmarků | výborný research prototype, částečně použitelný | extrémně vysoká | 4/4/5/4/3/3/3/5 | citeturn37view0turn38view0turn38view4turn39view0turn39view5 |
| DSPy MIPROv2 | evaluator-guided bounded adaptation / LM programs / open | instrukce + few-shot demonstrace pro predictor(y) | explicitní uživatelská metrika na valsetu, minibatch + pravidelný full-val | vrací nejlepší konfiguraci na full validation; Bayesian optimization | nejlepší současná praktická disciplína pro bounded improvement | zlepšuje prompt/program policy, ne core codebase; odolnost vůči gaming je jen tak dobrá jako metrika | zralé a dnes použitelné | extrémně vysoká | 5/4/5/5/3/5/5/5 | citeturn25view2turn25view1turn25view0turn25view3 |
| DSPy GEPA | evaluator-guided bounded adaptation / trace-aware optimizer / open | textové komponenty systému; v DSPy prompty, signatury, moduly; v repo i obecné text artifacts | skóre + volitelný text feedback; trainset + valset; Pareto tracking | budget caps přes metric calls/full evals; valset explicitně doporučen kvůli generalizaci | silná auditovatelnost, trace-based feedback, explicitní warning před overfittingem | když je metrika slabá nebo LLM-judge měkký, zhorší se i celý optimizer | zralé a dnes použitelné | extrémně vysoká | 5/4/4/5/3/4/4/5 | citeturn24view0turn33view3turn33view4turn24view3turn24view4 |
| AFlow | workflow search / agentic workflow generation / open | workflow topologie, operator sequence, node orchestration | evaluator nad validačními tasky; optimal workflow pak testován na test datasetu | validation trajectories, early stop, validation rounds; search přes MCTS | hledá workflow jako kód, ne mystický prompt | README přiznává migration bugs u operators; slabší governance a vyšší reprodukční tření | slibné, ale nedospělé | vysoká | 4/3/3/4/3/3/2/4 | citeturn16view6turn21view0turn17view0turn22view1 |
| ADAS | agent architecture search / code-level meta-agent / open | kód agentů a jejich design patterns | fitness na valid setu, bootstrap confidence interval; zvláštní evaluate fáze na test splitu | valid/test oddělení existuje, ale archive appenduje generované kandidáty bez tvrdého accept gate | důležitý historický krok od promptů ke kódově definovaným agentům | fixed outer meta-loop; slabá reject discipline; hodně „interestingness“, méně governance | výzkum, částečně použitelný | vysoká | 3/2/3/4/2/2/3/4 | citeturn16view2turn19view1turn20view0 |
| OPRO | prompt optimization / narrow / open | instrukce/prompty | skórované iterace na train, separátní evaluation script na test | nové kandidáty se přidávají do promptu s jejich hodnotami; test eval je odděleně | jednoduché, explicitní, levnější než plná architektura search | úzké, benchmarkové, slabší anti-regression než DSPy | použitelné dnes, ale úzce | střední | 4/3/4/5/2/3/4/4 | citeturn31view1turn31view2 |
| Promptbreeder | prompt evolution / narrow / paper-first | task-prompts i mutation-prompts | fitness na training setu | evoluce populace promptů; selekce přes fitness | chytrý self-referential nápad, důležitý historicky | slabší provozní disciplína, v primárních zdrojích slabší reprodukční opora než u DSPy/OPRO | zajímavý výzkum, ne základ architektury | střední | 3/2/3/4/2/2/2/3 | citeturn31view0 |
| ExpeL | experience-memory adaptation / environments / open | natural-language insights a few-shot recall strategy | success/failure v prostředí, eval stage na benchmark envs | experience gathering → insight extraction → evaluation; spíš kumulativní než tvrdě reject-based | relevantní pro „memory as non-truth continuity“ | slabá regression discipline pro změny architektury; méně deterministické | použitelné částečně v taskových envs | střední | 3/2/3/4/3/3/3/3 | citeturn28view0turn29view0turn29view4turn29view7 |

### Kontrolní a varovné systémy

| Systém | Verdikt | Proč je důležitý | Co JEFF má vzít | Co JEFF má odmítnout | Zdroje |
|---|---|---|---|---|---|
| SWE-agent a mini-SWE-agent | **kontrolní skupina reality, ne self-improvement** | ukazují, že externí harness a ACI často přinese víc než „reflexe“; zároveň 100-line agent s vysokým Verified score je varování před benchmark saturation | repo-level tooling, ACI, deterministické test harnessy | brát Verified leaderboard jako proxy robustnosti | citeturn27search0turn10view4turn27search8turn6view12 |
| CRITIC | **užitečný repair loop** | používá tool-interactive critique a externí feedback | externí nástroje jako lokální soudce | zaměnit output repair za persistent self-improvement | citeturn32view6turn32view7 |
| Reflexion | **hybrid; snadno sklouzne k hype** | umí pracovat s external feedback signals, ale často se prodává šířeji, než unese | episodic memory z externího feedbacku | prodávat reflexi jako robustní dlouhodobou adaptaci sama o sobě | citeturn32view0turn32view1turn32view2 |
| Self-Refine | **není self-improvement framework** | tentýž model generuje, kritizuje i opravuje | nic jako acceptance authority | cokoli bez externího soudce a regressions | citeturn32view3turn32view4turn32view5 |
| Self-Debugging | **silný lokální debug pattern** | execution results umí zlepšit code outputs | execution feedback a explanation-based debugging | vydávat to za persistent agent learning | citeturn32view9 |
| TextGrad | **zajímavý optimizer, ale evaluator je často měkký** | „textual gradients“ jsou užitečné, pokud objective skutečně něco měří | trace-informed feedback pro nepřímou optimalizaci | modelové pseudo-gradienty bez tvrdého acceptance gate | citeturn33view0turn33view1turn33view2 |

## Hloubkové rozbory nejrelevantnějších systémů

### Huxley-Gödel Machine

HGM je zatím nejzajímavější pokračování linie DGM, protože se nesnaží jen „dělat víc self-modifikací“, ale útočí na hlubší problém: **metaproductivity-performance mismatch**. Autoři tvrdí, že běžné self-improving coding agents preferují rodiče s vyšším aktuálním benchmark score, ale to nemusí znamenat vyšší potenciál pro další zlepšování. Proto zavádějí CMP, metrický odhad „slibnosti clade“, tedy celého podstromu potomků, a podle něj řídí expanzi stromu self-modifikací. Na papíře je to správný směr: oddělit „kdo je teď nejlepší coder“ od „kdo je nejlepší rodič pro další generace“. Prakticky je to stále benchmark-driven coding lab nad SWE-bench Verified a Polyglot, s veřejným repem, Docker sandboxem a explicitním varováním před spouštěním model-generated code. To je skutečný výzkum, ale pořád výzkum. JEFF by si z HGM měl vzít hlavně **myšlenku oddělit výkonnostní score od future-improvement score** a zcela odmítnout implicitní představu, že benchmark winner je automaticky nejlepší kandidát pro další samostatnou evoluci. citeturn40view2turn41view0

### Darwin Gödel Machine

DGM je dnes nejznámější skutečný self-modifying coding agent. Paper i repo popisují archiv agentů, z něhož se vzorkuje rodič; foundation model pak vytváří „new, interesting version“ rodiče a systém změnu empiricky validuje na coding benchmarcích. To je důležitá věc: nejde o čistou introspekci, ale o **patch → harness → score**. Repo navíc ukazuje konkrétní mechaniku, ne jen slidy. DGM vybírá cíle z unresolved ids, empty patches, stochasticity a context-length failure modes; kandidátní patch validuje přes SWE-bench Verified/Polyglot harness; přidává small/medium/full evaluation heuristiky; archiv může být aktualizován buď `keep_all`, nebo `keep_better`. Problém je v tom, že tenhle evaluator stack je pořád slabší, než název napovídá. DGM přímo načítá `princeton-nlp/SWE-bench_Verified`, používá veřejný benchmark a výchozí archivní režim je v kódu `keep_all`, tedy nikoli tvrdé „accept only if improved“. I `keep_better` porovnává kandidáta vůči baseline minus noise leeway, nikoli proti plnému regresnímu panelu a ne proti každému relevantnímu předku. To znamená, že DGM je skvělá laboratoř pro generator-search nad scaffoldem, ale ne model provozní důvěry. JEFF si z toho má půjčit archiv diffů, metadata, explicitní failure buckets a sandboxing; rozhodně nemá převzít volnou archivaci ani benchmark-only selekci jako finální autoritu. citeturn7view7turn18view0turn19view0turn9view7turn6view12

### SICA

SICA je možná nejzdravější self-modifying coding agent pro JEFF právě proto, že není tak nafouknutý. Paper popisuje jednoduchou, ale poctivou smyčku: archiv předchozích agentů a jejich benchmark výsledků, výběr best-performing agenta jako meta-agenta, návrh a implementace zlepšení, nová evaluace a znovu archivace. Rozdíl proti čistému leaderboard fetishismu je zásadní: „best“ je definován utility funkcí, která kombinuje benchmark performance, wall-clock time a dollar cost. SICA navíc obsahuje asynchronous overseer, který periodicky sleduje běh a může zasáhnout nebo exekuci zrušit při patologickém chování. A repo jde dál než papír: výsledky organizuje po iteracích tak, aby šlo ručně kontrolovat agent code, benchmark results, traces i meta_improvement logs. Tohle je auditovatelnost, kterou JEFF chce. Slabina je ale stejně jasná: experimentální důkazy stojí na náhodném subsetu SWE-Bench Verified, repo samo přiznává potřebu snížit variance a najít realističtější benchmarky a celé nastavení je pořád research prototype, ne hardened deployment framework. JEFF by si měl téměř přímo půjčit SICA-style result bundle a overseer jako monitor, ale nikdy ne jako finálního selektora změn. citeturn37view0turn38view0turn38view4turn39view0turn39view5

### DSPy MIPROv2

MIPROv2 je v tomto reportu záměrně vysoko, i když není „recursive self-improver“ v romantickém smyslu. Pro JEFF je ale mnohem cennější než většina těchto romantických systémů. Dokumentace říká přesně, co se optimalizuje: instrukce a few-shot demonstrace pro každý predictor v LM programu. Je tam explicitní `metric`, `trainset`, `valset`, minibatch search, full-validation checkpointy a návrat toho, co bylo **nejlepší na full validation setu**, ne jen nejlepší v jedné šťastné zkoušce. Paper doplňuje, že MIPRO používá stochastic mini-batch evaluation a meta-optimization procedure pro návrh instrukcí. Tohle je bounded evaluator-centered improvement v čisté podobě. Je to auditovatelné, replikovatelné, levné proti self-modifying code loops a pro JEFF prakticky použitelné hned: na prompty, tool routing, retrieval heuristiky nebo decomposition policies. Pokud JEFF chce začít chytře a ne jako benchmarkový klaun, MIPROv2 je jeden z nejlepších startů. citeturn25view2turn25view1turn25view0turn25view3turn25view4

### DSPy GEPA

GEPA je v jistém smyslu MIPRO pro tvrdší terén. Dokumentace i paper popisují reflective evolutionary optimizer, který bere nejen scalar score, ale i text feedback, zachytává full execution traces a pracuje s Pareto frontou kandidátů. Klíčové pro JEFF je, že GEPA má explicitní budget gate: přes `max_metric_calls`, `max_full_evals` nebo preset auto budgets. A ještě důležitější je explicitní warning v dokumentaci: bez odděleného valsetu prompt optimizer prompty prostě přeoptimalizuje na trainset. Tohle je přesně ta míra brutal honesty, kterou v agent hype ekosystému skoro nikdo nemá. GEPA má ale i riziko: pokud je samotná metrika měkká, nebo pokud se text feedback opírá o slabého LLM-judge bez deterministických backstopů, celý optimizer jen velmi efektivně maximalizuje špatný cíl. Proto je GEPA pro JEFF fantastický vzor pro **bounded proposal search**, ale ne pro **nezávislé přijetí změny**. Přijímat musí stále zvláštní eval/selection vrstva. citeturn24view0turn33view3turn33view4turn33view5turn24view3turn24view4

### AFlow

AFlow je zajímavý tím, že se nesnaží jen adjustovat prompt, ale reprezentuje workflow jako kódový search space a optimalizuje ho variantou Monte Carlo tree search. README výslovně popisuje node/operator/workflow/optimizer/evaluator rozdělení, validační trajektorie a „optimal workflow“ uložený odděleně s odpovídajícími test dataset výsledky. To je dobře: **proposal, search και evaluation jsou alespoň konceptuálně oddělené**. Současně ale README varuje, že některé operátory mohou mít bugs během migrace z MetaGPT. To zní banálně, ale pro JEFF je to přesně ten typ detailu, který odlišuje hezký paper od systému, kterému lze svěřit governance-citlivou smyčku. AFlow je slibný nástroj pro sandboxovaný workflow search nad interními tasks. Není to architektura, které byste dnes měli věřit pro samočinné změny produkčního core. citeturn16view6turn21view0turn17view0turn22view1turn16view9

### ADAS

ADAS je důležitý hlavně historicky a metodologicky. Ukázal, že agent designs jde generovat **v kódu**, ne jen prompt hackovat. Raw `search.py` zároveň ukazuje jeho silné i slabé stránky otevřeněji než většina paperů. Během search mode se hodnotí na validation části datasetu; během evaluate mode na oddělené test části; fitness je bootstrap confidence interval nad výsledky. To je dobré. Jenže archiv v praxi appenduje nové solutions poměrně volně a outer meta-loop je fixed. Jinými slovy: ADAS je lepší než prompt cosplay, ale anti-regression disciplina je slabší než u MIPROv2 nebo GEPA a governance je skoro nulová. Pro JEFF je z ADAS cenné hlavně to, že **agent architecture může být explicitně searchovatelný artefakt**. Není ale rozumné přebírat jeho volnější acceptance styl. citeturn16view2turn19view1turn20view0

### ExpeL

ExpeL je pro JEFF relevantní z úplně jiného důvodu než DGM nebo SICA. ExpeL neslibuje, že agent sám přepisuje vlastní kód do nekonečna. Místo toho sbírá zkušenosti z training tasks, extrahuje z nich natural-language insights a při inference si je znovu vytahuje. Repo to dělí na tři explicitní fáze: experience gathering, insights extraction a evaluation. To je rozumné. A právě proto je ExpeL užitečný pro JEFF jako vzor pro **kontinuitu bez pravdivostního nároku**: zkušenosti lze ukládat, strukturovat, používat, ale nemají být automaticky povýšeny na truth state. Slabina je, že chybí tvrdý accept/reject mechanismus pro samotnou architekturu a environmentálni feedback je méně deterministický než regression suite nad kódem. ExpeL je dobrý pattern pro non-truth memory, ne pro self-modification trust core. citeturn28view0turn29view0turn29view4turn29view7

## Rozsudek o spolehlivosti

### Kdo je skutečně evaluator-centered

Pokud přísně trváme na tom, že změna musí projít **explicitním soudcem**, pak nejlépe dopadají **MIPROv2** a **GEPA**. Nejsou nejvíc sexy, ale mají nejlepší provozní disciplínu: metrika je explicitní, budget je explicitní, train/val oddělení je explicitní, full validation checkpoint je explicitní a overfitting risk je explicitně přiznaný. To je přesně to, co chcete, když máte systém, kterému záleží na operator trust a auditovatelnosti. Naopak celý marketing okolo „recursive“ a „Gödel“ často dodává větší rétoriku než governance. citeturn25view2turn25view1turn24view0turn33view3

### Kdo má reálnou anti-regression disciplínu

Ze self-modifying coding agents má nejlepší konfiguraci anti-regression myšlení **SICA**, protože neřeší jen raw score, ale utility přes výkon, cenu a čas, a navíc zavádí overseer a archivuje detailní výsledky. **DGM** má compile filter, subset-based escalating eval a archiv, ale jeho výchozí `keep_all` je pro trust-sensitive prostředí příliš měkké. **HGM** je koncepčně lepší než DGM ve výběru, protože útočí na chybný search heuristic, ne na symptomy. Jenže ani HGM benchmark problém nevyřeší, pouze s ním sofistikovaněji pracuje. citeturn38view0turn38view4turn39view0turn18view0turn19view0turn40view2turn41view0

### Kdo hackuje benchmark nebo je k tomu nebezpečně blízko

Tady je potřeba říct to natvrdo. Vše, co v roce 2026 staví svůj hlavní „wow“ claim na SWE-Bench Verified, si musí nést obrovský otazník. Audit od entity["company","OpenAI","ai company"] tvrdí, že Verified je kontaminovaný a že významná část audited failures je ve skutečnosti chyba testů, ne schopnosti modelu. Samotný SWE-bench ekosystém mezitím posouvá část evaluace k privátním splitům a cloudovému vyhodnocení a vedle toho vznikají SWE-Bench Pro a continuously evolving decontaminated SWE-rebench. Když navíc oficiální tým SWE-agentu veřejně říká, že mini-SWE-agent má vysoké Verified skóre v zhruba 100 řádcích Pythonu, je to spíš varování než triumf: ten benchmark už značně měří i to, jak dobře se komunita naučila benchmark exploatovat, ne jen obecnou software engineering robustnost. citeturn6view12turn6view11turn35search20turn6view14turn10view4turn27search8

### Kdo je jen recursive rhetoric

**Self-Refine** není špatný decoding pattern. Ale pokud je prodáván jako self-improving system, je to nesmysl. Generátor, kritik i opravář jsou tentýž model. **Reflexion** je užitečnější, když má skutečný task feedback, ale není to automaticky dlouhodobě spolehlivý improvement system. Kritická práce o self-correction bez externího feedbacku tomu dává poslední hřebík: bez externího soudce se reasoning často nezlepší a někdy se zhorší. Takže ano, reflection může být součást evaluator loopu. Ne, reflection sama o sobě evaluator loop není. citeturn32view3turn32view0turn32view1turn32view4turn32view5

### Kdo má smysluplný holdout a kdo ne

Smysluplné oddělení search a holdout signal mají **MIPROv2**, **GEPA** při použití valsetu, **AFlow**, **ADAS** a částečně **OPRO**. **ExpeL** má training tasks a následnou eval fázi, ale není to architektonicky tak tvrdé jako validation-driven optimizers. **DGM**, **HGM** a **SICA** mají evaluátory reálné, ale odpovídající holdout discipline je slabší nebo benchmarkově problematická kvůli veřejnému SWE-bench setupu. Jinak řečeno: existuje rozdíl mezi „měřím něco“ a „měřím něco, co nezkolabuje při prvním styku s benchmarking reality drift.“ Většina hype projektů ten rozdíl nezná. citeturn25view2turn24view0turn21view0turn20view0turn31view2turn29view0turn6view12

## Should JEFF pursue bounded self-improvement?

Ano. Ale pouze v omezené, evaluator-first, operator-approved podobě. Cokoli širšího by bylo předčasné a hloupé. JEFF už podle repozitáře stojí na tom, co tento směr potřebuje: truthful inspection, bounded execution, approval-gated continuation a anti-drift mindset. To je vhodný základ pro **laboratorní refinement loop**, nikoli pro široce autonomní samovývoj. citeturn40view0

JEFF by měl v blízkém horizontu zkusit pouze **bounded self-improvement of non-truth-critical surfaces**. Konkrétně: prompty pro research subtasky, tool routing, retrieval strategy, decomposition heuristiky, případně izolované patch-laby pro pomocné moduly. Neměl by se dotknout pravdivostního modelu stavu, approval vrstvy, core governance, audit logiky ani mutačních pravidel kolem truth transitions. Tyto vrstvy musí zůstat mimo rozsah v1, protože právě tam se benchmarkové divadlo nejrychleji mění v produkční sebeklam. citeturn25view2turn24view0turn37view0turn6view12

Než JEFF udělá byť jediný krok směrem k self-improvement, musí mít hotových několik předpokladů. Musí mít **fixní evaluator stack**, který je oddělený od generátoru kandidátů. Musí mít **deterministické regresní testy** pro každý improvement surface. Musí mít **holdout task sety**, které se nekrmí zpátky do search loopu. Musí mít **cost/latency/success utility**, ne jen jedinou accuracy metriku. Musí mít **inconclusive state**, aby neinterpretoval šum jako zlepšení. A musí mít **operator-facing diff bundle**, jinak není audit, jen víra. Tohle nejsou nice-to-haves. Bez toho je self-improvement jen dražší forma promptového sebepřesvědčování. citeturn38view0turn25view2turn24view0turn33view3

Lidské schválení musí zůstat povinné minimálně pro pět věcí: změna cílové utility, změna evaluatoru, změna benchmark registry, změna acceptance threshold a jakákoli změna modulu, který může mutovat truth state nebo operator-facing governance. Pokud se JEFF pokusí tuto hranici obejít, ztratí to, co ho dělá zajímavým: trustworthy operator visibility. A bez toho už to není JEFF, ale další benchmarkový cirkus se sebevědomým README. citeturn40view0turn38view4

## Návrh omezeného vzoru pro JEFF

Evidence tento krok ospravedlňuje, ale jen v přísně sevřené formě. Doporučený JEFF-kompatibilní pattern má vypadat takto:

1. **Vyber jediný improvement surface.**  
   Například retrieval prompt, task decomposition policy nebo router mezi dvěma nástroji. Ne core truth semantics, ne operator approval logic, ne mutation rules pro stav.

2. **Zmraz baseline.**  
   Vytvoř verzi kandidáta, evaluatoru, benchmark registry, seedů a truth-state snapshotu. Improvement loop nesmí měnit evaluator ani benchmark během běhu.

3. **Odděl proposer od selectoru.**  
   Proposer agent smí jen navrhovat kandidátní prompt, konfiguraci nebo patch. Selector smí jen číst evidence bundle a aplikovat acceptance policy. Tyto role nesmí splývat.

4. **Generuj kandidáty v izolaci.**  
   Každý kandidát běží v sandboxu nebo branchi. Žádná změna se nesmí propsat do živého runtime ani truth state.

5. **Spusť statické a deterministické kontroly.**  
   Syntax, lint, type checks, unit tests, schema checks, tool-contract checks. Pokud něco padne, výsledek je **regression**, ne „možná se to zlepší příště“.

6. **Spusť holdout eval.**  
   Měř minimálně tři osy: task success, p95 latency, cost per task. Pro truth-sensitive subflows přidej exactness/consistency checks. Pokud je evaluátor modelový judge, musí být pouze doplňkový, nikdy ne jediný.

7. **Klasifikuj výsledek do pěti stavů.**  
   - **success**: splněny všechny hard gates, utility nad baseline  
   - **partial success**: primární metrika lepší, ale vedlejší budget těsně horší  
   - **degraded success**: accuracy nahoru, ale cena/latence/trust výrazně dolů  
   - **inconclusive**: variance překrývá baseline nebo běh je nestabilní  
   - **regression**: fail deterministického checku nebo holdout propad  
   Jen `success` má být automaticky kandidát na review. `partial success` jen s explicitní operátorskou výjimkou. `degraded`, `inconclusive` a `regression` fail closed.

8. **Aplikuj tvrdé acceptance thresholdy.**  
   Pro první JEFF smyčky doporučuji něco přísného:  
   - nula kritických regresí v deterministických testech  
   - zlepšení utility alespoň o předem daný margin na holdoutu  
   - max +10–15 % na cost nebo latency, podle povahy povrchu  
   - opakovatelnost přes více seedů nebo opakovaných běhů  
   Bez splnění všech hard gates se kandidát pouze archivuje, nedeployuje.

9. **Předlož operátorovi evidence bundle.**  
   Balík musí obsahovat: diff, proč byl navržen, trace evaluace, benchmark subsety, seed, utility breakdown, seznam regressions, cost report a rollback id. Pokud to člověk neumí zkontrolovat za pár minut, systém ještě není dost auditovatelný.

10. **Nasazuj jen řízeným rolloutem.**  
    Nejdřív canary, potom omezený scope, potom širší deploy. Každá nasazená změna musí mít automatický rollback path.

11. **Zakázat tichou truth mutation.**  
    Přijatá zlepšení mohou měnit prompt, config nebo kód izolovaného modulu. Nesmí sama měnit JEFF truth state. Truth mutation musí zůstat explicitní, přechodová a oddělená.

12. **Logovat všechno jako evidence, ne jako pravdu.**  
    Memory z improvement loopu je continuity artifact, ne truth artifact. Změna byla navržena, vyhodnocena, přijata a nasazena na základě evidence. To je historie. Ne ontologie. citeturn25view2turn24view0turn38view0turn39view0turn18view0turn19view0turn6view12

Tohle je pro JEFF realistické. Cokoli ambicióznějšího typu „agent si sám přepíše governance a ráno bude chytřejší“ je zatím architektonický brak.

## Závěrečná doporučení

### Top ideas, které má JEFF převzít

1. **Explicitní externí evaluator jako první-class komponentu**, ne jako post-hoc dashboard. MIPROv2 a GEPA jsou v tomhle správný vzor. citeturn25view2turn24view0
2. **Train/val nebo search/holdout separaci** pro každou optimalizační smyčku. Bez ní si systém plete učení s opisováním. citeturn25view2turn33view3
3. **Budget ceilings** na metric calls, full evals, cenu a čas. Výbušná smyčka není „otevřená evoluce“, ale špatně navržený provoz. citeturn33view3turn17view0
4. **Best-on-full-validation selection**, ne best-of-many cherry-pick. citeturn25view2
5. **Utility přes úspěch + cenu + latenci**, ne single-score fetish. SICA je tady lepší než většina self-improvement paperů. citeturn38view0
6. **Archiv diffs, benchmark výsledků a trace bundle** pro každou přijatou změnu. SICA i DGM ukazují, proč je to nutné. citeturn39view0turn18view0
7. **Failure buckets** typu empty patch, stochasticity, context overflow místo vágního „agent failed“. DGM je tady prakticky poučný. citeturn18view0
8. **Asynchronní oversight jako monitor**, nikoli jako naslepo důvěřovaný soudce. SICA to trefuje relativně dobře. citeturn38view4
9. **Memory jako evidence continuity, ne truth mutation.** ExpeL je užitečný vzor pro inspectable lessons. citeturn28view0turn29view4
10. **Explicitní stav `inconclusive`**. Pokud to chybí, systém bude šum číst jako progres. To je jedna z nejčastějších cest do benchmarkového sebeklamu. citeturn25view2turn6view12

### Top ideas, které má JEFF odmítnout

1. **Reflection-only acceptance**. Bez externího soudce to není improvement. Je to sebemluva. citeturn32view3turn32view4
2. **Public benchmark jako jediný acceptance gate**, zvlášť když je kontaminovaný nebo testově vadný. citeturn6view12turn35search20
3. **Skrytou autonomii** při nasazování změn do trust core.
4. **Auto-generated benchmarky jako jediný důkaz zlepšení.**
5. **Best-of-many leaderboard reporting bez variance a cost reportu.**
6. **Archive-all bez tvrdého selector policy.** U DGM je to dobré pro search diversity, špatné pro provozní důvěru. citeturn18view0
7. **Confusing memory with truth.**
8. **LLM-judge jako jediný rozhodčí** u truth-sensitive pathways.
9. **Recursion branding** bez bounded stop conditions a rollback cesty.
10. **Tiché přepisování governance, approval a truth mutation logiky.** Pokud tohle povolíš, je po důvěře.

### Top papers a repozitáře hodné seriózního studia

1. **SICA: A Self-Improving Coding Agent** — nejlepší kombinace utility-based acceptance, auditovatelných logů a praktické relevance pro JEFF. citeturn37view0turn39view0
2. **Darwin Gödel Machine** — nejdůležitější referenční implementace skutečné benchmark-driven self-modification, i když benchmarkově problematická. citeturn7view7turn18view0turn19view0
3. **Huxley-Gödel Machine** — nejzajímavější korekce DGM-style searchu díky CMP a metaproductivity framingu. citeturn40view2turn41view0
4. **DSPy MIPROv2** — nejlepší praktický template pro bounded evaluator-guided refinement. citeturn25view2turn25view1
5. **DSPy GEPA** — nejsilnější trace-aware optimizer s explicitním overfitting warningem a budget discipline. citeturn24view0turn33view3

### Top systems pro malý kontrolovaný prototyp

1. **MIPROv2** pro prompty a decomposition policies v nepravdivostních subflow JEFFu.  
2. **GEPA** pro evaluator-guided refinement tam, kde lze vracet i textové diagnostické feedbacky z trace.  
3. **SICA-style patch lab** pro izolovaný pomocný modul JEFFu, ale pouze se samostatným evaluátorem, striktní review branou a nulovou možností mutovat truth core. citeturn25view2turn24view0turn39view0turn38view0

### Finální verdikt

Evaluator-centered self-improvement je **dost zralý pro architektonické použití**, pokud tím myslíte omezené a auditovatelné refinement smyčky nad prompty, workflow, routingem nebo izolovanými helper moduly. Není dost zralý pro širokou autonomní self-modification systému, kterému záleží na truth, governance a operator trust. Nejlepší systémy v oboru nejsou ty, které nejhlasitěji mluví o rekurzi. Nejlepší jsou ty, které umí říct **co přesně se změnilo, kdo to změřil, proč to prošlo, co se nezhoršilo, kolik to stálo a jak to vrátit zpět**. Pokud JEFF tuhle disciplínu udrží, bounded self-improvement dává smysl. Pokud ne, bude z toho jen další sebevědomý benchmarkový podvod s hezkým názvem. citeturn40view0turn25view2turn24view0turn38view0turn6view12