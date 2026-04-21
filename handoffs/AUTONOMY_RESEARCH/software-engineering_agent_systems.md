# Technický výzkum evaluačně řízených coding-agent smyček pro JEFF

## Souhrn

Nejdůležitější závěr je nepohodlný, ale jasný: u software-engineering agentů dnes nevyhrává „víc agentů“, „větší kontext“ ani hezčí demo. Vyhrává tvrdá externí evaluace. Tam, kde systém opravdu staví smyčku na reproduktoru chyby, testech, buildu, lintu, statické analýze nebo benchmarkovém graderu, je obvykle poctivější, lépe laditelný a méně náchylný ke kecání. To přesně sedí na Agentless, AutoCodeRover, mini-SWE-agent a na interaktivní harnessy typu aider, pokud jsou připojené k reálným testům. Naopak tam, kde „verifikace“ znamená hlavně modelový reviewer nebo neurčitý reflexivní prompt, je spolehlivost dramaticky slabší. I entity["organization","Anthropic","ai company"] u agent evalů explicitně říká, že pro coding agenty jsou přirozeným zlatým standardem deterministické gradery, tedy hlavně testy a běžící software. citeturn8search7turn11search5turn17search3turn16search0turn34view0

Systémy, které má smysl respektovat, nejsou nutně ty nejvíc flashy. mini-SWE-agent je brutálně jednoduchý a právě to je jeho síla: lineární historie, bash-only, žádný křehký stavový shell, explicitní step a cost limity a dobře prohlížitelné trajektorie. SWE-agent přinesl důležité patterny jako retry meta-agent, chooser a trajektorie, ale jeho vlastní dokumentace už dnes doporučuje přejít na mini-SWE-agent a označuje SWE-agent za maintenance-only. Agentless je méně „agentic“ a o to víc poctivý: lokalizace, oprava, patch validation. AutoCodeRover je technicky silný tam, kde lze chybu reprodukovat a využít fault localization. OpenHands je dnes nejbohatší otevřená platforma pro skládání těchto smyček, ale jeho nejzajímavější verifier stack je stále explicitně experimentální. citeturn25view0turn32search1turn26view0turn17search1turn17search3turn16search0turn28view1turn28view2

Prakticky použitelné dnes jsou čtyři třídy věcí. Za prvé interaktivní pair-programming harnessy s rollbackem a test hooks, hlavně aider. Za druhé minimalistické benchmark/workbench smyčky typu mini-SWE-agent. Za třetí produkčněji laděné harnessy s povoleními a sandboxem, tedy Claude Code a Codex CLI, ale jen pokud je donutíte používat externí evaluaci. Za čtvrté OpenHands, pokud ho berete jako SDK a ne jako magického autonomního vývojáře. Co dnes jako samostatný cíl studia už nedává smysl, je OpenDevin: archivovaný účet sám odkazuje na OpenHands. A co je zatím hlavně výzkumná hračka, jsou self-improving benchmarkové smyčky jako SICA, Darwin Gödel Machine a Live-SWE-agent. Jejich outer loop je sice tvrdě evaluační, ale operátorsky důvěryhodný produkt z toho ještě není. citeturn15search1turn20search18turn38view0turn36view0turn28view0turn8search0turn9search0turn8search6

Pro JEFF je dobrá zpráva, že jeho současné směřování je ve skutečnosti správnější než velká část trhu. README popisuje JEFF jako CLI-first, persisted-runtime backbone se „truthful inspection“, bounded `/run`, approval-gated continuation a anti-drift coverage; navíc explicitně říká, že `/run` není obecný command runner, ale jedna ohraničená validační smyčka s fixním smoke pytest plánem. To je strukturálně poctivější základ než většina agentic marketingu. JEFF by tedy neměl kopírovat slavné agenty. Měl by ukrást jen to, co je tvrdé: deterministické brány, rollback, trajektorie, checkpointy, oddělený reviewer, sandbox a jasné stavy „nevíme“, „neprovedeno“, „provedeno ale neověřeno“, „ověřeno“, „vyžaduje schválení“. citeturn12view0turn13view0turn33view1turn38view2turn36view1turn37search1

## Taxonomie evaluačních smyček u coding agentů

**Test-gated edit loops** jsou nejpraktičtější a pro JEFF nejcennější. Smyčka je jednoduchá: načti kontext, uprav soubory, spusť test/lint/build, oprav podle výsledků, skonči při průchodu nebo eskaluj. aider to dělá explicitně přes `--test-cmd`, `--auto-test`, linting a `/undo`; Claude Code a Codex to umějí také, ale jen pokud jim testy a hooky řeknete napřímo. Síla evaluátoru je zde **silná až střední** podle kvality test stacku. citeturn34view0turn33view1turn38view1turn38view0turn36view3turn36view5

**Planner–executor–verifier loops** oddělují čtení a návrh od mutace. OpenHands už má veřejný dvoufázový příklad: planning agent s read-only nástroji a execution agent s plnými editačními právy. Claude Code má plan mode, kde agent nejprve ukáže plán a čeká na schválení. To je pro JEFF architektonicky výborný pattern, protože plán není ještě povolení k akci. Síla evaluátoru je zde **střední**, pokud za plánovací fází stojí až následná tvrdá validace; jinak rychle sklouzne do divadla. citeturn28view3turn38view3turn13view0

**Localization → repair → patch validation pipelines** jsou méně sexy, ale často poctivější než obecné „agentic“ smyčky. Agentless výslovně používá tři fáze: lokalizaci, opravu a patch validation; AutoCodeRover jde dál přes reprodukci chyby, fault localization, inferenci specifikace a validaci patche testy. Tady je evaluátor obvykle **silný**, protože rozhodující signál nepřichází z vlastní sebereflexe modelu, ale z vnějšího checku. Slabina je, že to funguje hlavně tam, kde check existuje. citeturn17search3turn17search22turn16search0turn16search3turn16search5

**Reviewer-mediated patch loops** přidávají mezi patch a akceptaci ještě review vrstvu. U OpenHands je to critic, který vrací score a může spouštět iterative refinement; u Codexu je `/review`, který spustí odděleného review agenta bez zásahu do working tree; v literatuře sem patří SpecRover a R4P. Tento pattern je užitečný jako druhá nebo třetí vrstva, ale jako primární evaluator je **slabý až střední**. Důvod je drsný: OpenHands sám ukazuje, že kritici trénovaní jen na benchmarkových datech jsou na reálných outcome proxys skoro náhodní. citeturn28view1turn28view2turn31search1turn37search1turn22search1turn22search0

**Benchmark-driven repair loops** jsou v akademii dominantní. Typická forma je issue → patch → private evaluation → přijmi/odmítně, často přes SWE-bench. Tohle je výborné pro měření a reprodukovatelnost, ale ne pro operátorskou důvěru samo o sobě. SWE-bench skutečně aplikuje patch a spouští testy v Dockeru; Verified je lidsky validovaný subset 500 úloh. Jenže pozdější práce ukázaly, že leaderboard může být falešně nafouknutý kvůli nedostatečným testům a formálním issue promptům, které nereprezentují běžnou práci v editoru. citeturn11search5turn23search10turn23search1turn23search18turn23search6

**Self-improving benchmark loops** jsou outer-loop systémy, kde agent nebo scaffold upravuje sám sebe a změny se přijímají podle benchmarkového skóre. SICA, Darwin Gödel Machine a Live-SWE-agent sem spadají přesně. Na papíře jsou fascinující, protože mají explicitní evaluator. V praxi je to dnes ale skoro čistě výzkumná kategorie. Evaluátor bývá **silný na benchmarku**, ale **slabý pro operátorský trust**, protože akceptační kritérium je „lepší skóre“, ne „bezpečnější a pravdivější provoz v repo“. citeturn8search0turn9search0turn8search6

## Srovnávací tabulka kandidátů

Skóre je v pořadí: **EC/ES/U/FH/B/R/OI/AR** = evaluation clarity / evaluator strength / usability / failure honesty / boundedness / reproducibility / operator inspectability / architectural relevance pro JEFF.

| Systém | Doména | OSS | Tvar smyčky | Typ evaluátoru | Zralost | Dnes použitelné? | Silná stránka | Slabina | Relevance pro JEFF | Skóre | Zdroje |
|---|---|---:|---|---|---|---|---|---|---|---|---|
| mini-SWE-agent | lokální CLI a issue solving | otevřený | prompt → bash action → observation → exit; bounded step/cost | externí testy/benchmark; interně jen limity | aktivní OSS | Ano | minimální, inspectable, stabilnější díky nezávislým subprocess akcím | slabý built-in evaluator mimo explicitní test stack | velmi vysoká | 5/3/4/5/5/5/5/5 | citeturn25view0turn32search1turn7search1turn7search3 |
| SWE-agent | tool-rich benchmark/workbench harness | otevřený | agent + retry meta-agent + chooser | reproducer prompty, review-on-submit, benchmark testy | maintenance-only | Částečně | retry/chooser/trajectory patterny | složitost, křehkost, projekt sám doporučuje migraci na mini | vysoká | 4/3/3/4/4/4/5/4 | citeturn26view0turn27view0turn6search3turn6search15 |
| OpenHands | SDK/CLI/GUI platforma | otevřený + source-available části cloud produktu | CodeAct loop; max iterations; volitelně planner → executor; kritic/refinement | runtime observations, benchmark harness, volitelný critic | aktivní OSS platforma | Ano, ale s výhradami | composable SDK, sandbox, plánování, evaluator hooks | critic je experimentální; benchmarkové auto-user flow; známé stuck-loop bugy | velmi vysoká | 4/3/4/3/4/4/4/5 | citeturn28view0turn28view1turn28view2turn28view3turn30view0turn29view0turn29view1 |
| AutoCodeRover | repo-level issue repair | otevřený | reproduce → localize → infer spec → patch → validate | reproducer testy, SBFL, test suite | výzkumný, ale seriózní | Částečně | silná fault localization a explicitní validační pipeline | méně pohodlný pro běžné operátory; závislost na reprodukci | velmi vysoká | 5/4/2/4/4/4/2/5 | citeturn16search0turn16search3turn16search5 |
| Agentless | benchmark/workbench repair pipeline | otevřený | localization → repair → patch validation | syntax filter, regression testy, reproduction testy/rerank | výzkumný, ale velmi důležitý | Částečně | poctivá, jednoduchá a levná stage machine | slabší interaktivita, slabý UX pro operátora | velmi vysoká | 5/4/2/5/5/5/2/5 | citeturn17search1turn17search3turn17search22turn21search15 |
| aider | interaktivní pair-programming harness | otevřený | prompt → edit → lint/test → fix → commit/undo | lint, test cmd, build cmd, git rollback | aktivní OSS | Ano | nejlepší poměr použitelnost / rollback / eval integrace | není to autonomní issue resolver; plná kontinuita je stále spíš semi-manual | velmi vysoká | 4/3/5/4/5/5/5/5 | citeturn34view0turn33view1turn33view2turn35view0 |
| Claude Code | interaktivní terminal/IDE harness | uzavřený | gather context → act → verify; s plan mode a hooks | testy dle promptu; deterministické hooks; lidské approval | aktivní produkt | Ano | silné approval boundaries, deterministic hooks, checkpoints | defaultně není correctness fail-closed; hooky musí dodat tým | vysoká | 3/2/5/3/4/3/5/4 | citeturn38view0turn38view1turn38view2turn38view3turn38view4 |
| Codex CLI | lokální coding agent a review harness | otevřený | local agent loop; sandbox/approvals; optional scored loop; separate reviewer | externí eval skripty, hooks, reviewer agent, lidská review | aktivní produkt + OSS CLI | Ano | velmi dobrý trust model okolo sandboxu a review | correctness stále stojí na externím evaluatoru; hlášené sandbox/approval edge-case bugy | vysoká | 4/2/4/3/4/4/5/4 | citeturn36view0turn36view1turn36view3turn36view4turn37search1turn37search3turn19search6turn19search8 |
| SWE-Gym | training/eval harness pro agenty a verifiery | otevřený | env → rollout → execution-based reward/verifier → RL / rerank | exekuční validace, trénovaní verifiers | výzkumná infrastruktura | Částečně | explicitně řeší training agents **and verifiers** | není to hotový builder tool | vysoká | 5/4/2/4/5/5/3/5 | citeturn8search1turn8search13turn21search7 |
| Self-improving benchmark agents | výzkumné self-improvement smyčky | smíšené | agent upraví vlastní scaffold → benchmark → keep/discard | benchmark skóre | čistý výzkum | Ne | konečně mají hard outer evaluator | benchmark overfitting; mizerný operator trust | střední | 3/4/1/2/3/2/2/3 | citeturn8search0turn9search0turn8search6 |
| Reviewer/verifier components | verifier vrstvy | smíšené | trajectory/patch review → rerank/refine/early stop | LLM critic, rubriky, reviewer reasoning | experimentální až výzkumné | Částečně | rychlý doplňkový signál nad testy | špatný nápad jako jediná brána | středně vysoká | 4/2/2/2/4/3/4/4 | citeturn28view1turn28view2turn31search1turn22search0turn22search1 |

Poznámka k historickým jménům: OpenDevin je dnes archivovaný účet, který sám odkazuje na OpenHands. Jako samostatný systém už nestojí za cílené studium, leda kvůli historii projektu. citeturn15search1

## Hloubkové rozbory nejrelevantnějších systémů

**mini-SWE-agent** je pro JEFF možná nejdůležitější referenční bod právě proto, že odmítá spoustu „agentic“ balastu. Zdroják ukazuje jednoduchou smyčku `run()` → `step()` → `query()` → `execute_actions()`, bounded přes `step_limit` a `cost_limit`; stav je lineární a trajektorie se ukládá průběžně. Dokumentace navíc explicitně vysvětluje, proč se autoři vzdali stavového shellu: ukončování příkazů, rozbití shell session a nekonzistentní output považují za flakey problém a raději spouštějí každou akci jako nezávislý subprocess. To je strukturálně poctivé a pro JEFF extrémně cenné. Slabina je očividná: built-in evaluator je prakticky jen omezení rozpočtu; „správnost“ musí přijít zvenku, typicky přes repro script, testy nebo benchmark. Co ukrást: lineární historii, malý kontrolní tok, tvrdé limity, ukládání trajektorií a procesní izolaci. Čemu se vyhnout: bash-only svět jako jediný režim, pokud JEFF míří na složitější repo workflow. citeturn25view0turn32search1turn7search1

**SWE-agent** je důležitý spíš jako zdroj patternů než jako cíl adopce. Jeho konfigurace ukazuje explicitní postup „najdi relevantní kód → vytvoř reproducer → uprav zdroják → znovu spusť reproducer → zvaž edge cases“. Má `max_requeries` pro format errors, blocked actions a bash syntax errors a nad tím retry meta-agent, který může spustit víc pokusů a vybrat nejlepší. To je výborný pattern pro JEFFův modul „retry / revalidate / recover“. Jenže stejná dokumentace zároveň říká, že SWE-agent byl supersedován mini-SWE-agentem a je už jen maintenance-only. Issue tracker navíc ukazuje reálné smyčkové a parserové problémy v praxi. Co ukrást: retry meta-agent, chooser a trajektorii po pokusech. Co zahodit: monolitickou složitost a představu, že bohatší scaffold automaticky znamená robustnější scaffold. citeturn26view0turn27view0turn6search3turn6search15

**OpenHands** je dnes nejbohatší otevřená platforma, ale zároveň největší pokušení k architektonickému sebepodvodu. Pozitivní stránka: CodeAct agent má jasný tool surface, SDK podporuje plánovacího agenta s read-only nástroji a zvláštního execution agenta, evaluator harness má explicitní `max_iterations` a umí sbírat historii a metriky. Negativní stránka: jejich benchmark harness simuluje uživatele funkcí `user_response_fn`, která agentovi v evaluacích říká, ať „nikdy nežádá lidskou pomoc“ a prostě pokračuje nebo se vzdá; to je benchmarkově praktické, ale pro operator-trustworthy architekturu spíš smrad. Ještě tvrdší problém: critic je zajímavý a umí iterative refinement přes thresholdy, ale dokumentace ho označuje za „highly experimental“ a vlastní blog OpenHands přiznává, že kritici trénovaní jen na benchmark-style datech jsou na reálných outcome proxys skoro náhodní. Přidej k tomu veřejné stuck-loop issue a dostaneš přesně obraz systému, který je silný jako platforma, ale ne tak poctivý, jak by naznačovalo demo. Co ukrást: oddělení planner/executor, sandbox, evaluator API, vizualizované trajectories a schopnost přidat critic jako sekundární signál. Co nekrást: benchmarkové „fake user“ kontinuace a jakoukoli důvěru v model-only critic jako finální bránu. citeturn28view3turn30view0turn28view1turn28view2turn31search1turn29view0turn29view1

**Agentless** je pro JEFF zlatý referenční baseline, i když technicky není „agentic“ v módním smyslu. Paper to říká otvoreně: jde o jednoduchý třífázový proces lokalizace, opravy a patch validation bez autonomního tool-use rozhodování a bez komplikovaných interaktivních loops. Právě proto je to poctivé. Když systém neví, co je relevantní, selže v lokalizaci; když patch neprojde, nehraje divadlo úspěchu. Patch validation navíc zahrnuje jednoduché filtry na syntax a v dalších analýzách se ukazuje role reproduction testů pro lepší reranking. Co ukrást: pevnou stage machine, která odděluje „našli jsme místo“, „navrhli jsme patch“ a „patch externě prošel“. Co nekrást: úplnou absenci operátorského UX a slabou možnost interaktivního steeringu. JEFF nechce být benchmark batch runner; chce být důvěryhodný operátorský systém. citeturn17search1turn17search3turn17search22turn21search15

**AutoCodeRover** je nejblíž klasickému software-engineering přemýšlení. Začíná reprodukcí chyba, pak fault localization přes strukturální vyhledávání a volitelně Spectrum-Based Fault Localization, z issue a kódu odvodí spec-like kontext a teprve potom generuje patch. Nakonec patch validuje přes dostupné testy. Tohle je přesně ten typ smyčky, kde evaluace není kosmetika, ale nosná kostra. Je silnější než generický „prompt → edit → maybe test“ loop, protože má explicitní diagnostickou fázi a explicitní validační fázi. Kde se láme: pokud nejde problém dobře reprodukovat, pokud test suite není použitelný, nebo pokud jde o feature task bez jednoznačného chybového signálu, klesá hodnota celé pipeline. Co ukrást: reproducer-first disciplínu, fault localization jako samostatný modul a to, že evaluator rozhoduje o osudu patchů, ne naopak. Co nekrást: těžký bespoke analysis stack bez jasného důvodu. citeturn16search0turn16search3turn16search5

**aider** je dnes asi nejpoctivější praktický nástroj pro seriózní buildery, kteří chtějí produktivitu, ale nechtějí lhát sami sobě. Umí automaticky lintovat po editaci, umí pouštět test command a při non-zero exit kódu se pokusí chyby opravit, a celé to sedí na git integraci s `/undo` a auto-commity. To je extrémně důležité: rollback není teorie, je to jeden příkaz. Zároveň aider nepředstírá, že je plně autonomní repo resolver; hodně jeho síly je v tom, že člověk zůstává blízko difu a evaluatoru. Ve veřejných issue je i vidět, že kontinuální „běž build pořád dokola sám“ flow lidé chtějí, ale UX je stále hodně párovací, ne servo-smyčka. Pro JEFF je tentero pattern cenný: nehrát si na magii, ale přivést model do smyčky, kde po každé změně ihned následuje externí check a kde rollback je normální operace. Co ukrást: git-native undo, auto-lint, auto-test, jednoduché command contracts. Co nekrást: představu, že interaktivní pair-programmer sám o sobě řeší governance a truth boundaries. citeturn34view0turn33view1turn33view2turn35view0

**Claude Code** má velmi dobré operator-control patterny, ale vestavěná correctness story je slabší, než si lidi rádi namlouvají. Dokumentace popisuje agentic loop jako gather context → take action → verify. Má permission modes, včetně plan mode, kde agent popíše plán a čeká na approval před změnami; má checkpoints a `/rewind`; má hooks, které jsou výslovně deterministické a „guarantee the action happens“. To všechno je pro JEFF skvělé: plán není akce, hook je tvrdší než prompt, revert je levný. Zároveň ale checkpointing nesleduje změny udělané bash příkazy a samotná „verify“ fáze není built-in silný evaluator — agent typicky běží testy „pokud jsou k dispozici“ nebo pokud mu to přikážeš. Jinými slovy: na permissions je to poctivější než většina konkurence, na correctness ne. Co ukrást: plan mode, deterministic hooks, checkpoint/rewind. Co nekrást: implicitní důvěru, že „verify“ znamená „ověřeno“ i v repu bez tvrdých checků. citeturn38view0turn38view1turn38view2turn38view3turn38view4

**Codex CLI** je z veřejně doložených „Codex-style“ harnessů asi nejzajímavější tím, že má docela dospělý trust model okolo sandboxu, approvals a review. Je open source, běží lokálně, umí číst, měnit i spouštět kód ve vybraném adresáři. OpenAI dokumentace ukazuje sandbox jako technickou hranici autonomie a approval policy jako pravidlo, kdy se musí zastavit a zeptat. Zároveň umí `/review`, který spustí odděleného review agenta bez dotyku working tree, a oficiálně dokonce doporučuje „eval-driven improvement loop“ s externím skórovacím skriptem a reviewable artifacts. To všechno zní zdravě. Háček je přesně tam, kde ho čekáš: correctness není první-class hard gate sama o sobě; hard gate si musíš dodat. Dokonce i v issue trackeru jsou vidět sandbox a approval edge-cases. Co ukrást: oddělení sandbox boundary od approval boundary, odděleného reviewer agenta a eval-driven prompting patterned kolem externích skriptů. Co nekrást: spoléhat na to, že product docs o „scored loop“ automaticky znamenají, že evaluator už je pevnou součástí runtime. citeturn36view0turn36view1turn36view3turn36view4turn37search1turn37search3turn19search6turn19search8

## Soud o spolehlivosti

Kdybych to měl říct bez cukrování: pro JEFF jsou dnes nejspolehlivější ke studiu ty systémy, které se nebojí být nudné. Agentless a AutoCodeRover mají méně „agent personality“, ale víc skutečného software-engineering smyslu. mini-SWE-agent je záměrně chudý a právě proto auditovatelný. aider je prakticky nejlepší z interaktivních nástrojů, protože má reálnou test/lint smyčku a rollback. OpenHands je studovatelný jako platforma a SDK, ne jako pravda o autonomním vývoji. Claude Code a Codex jsou užitečné harnessy, ale bez repo-specific evaluator stacku z nich snadno uděláš zdroj velmi sebevědomých polopravd. citeturn17search3turn16search0turn25view0turn34view0turn28view0turn38view1turn36view3

Velká část benchmarkového prostoru je nafouknutá. To není názor, to je už doložený problém. SWE-bench sice zavedl důležitou patch-based exekuční evaluaci v kontejnerech a Verified je lidsky validovaný subset, ale UTBoost našel instance s nedostatečnými testy a stovky patchů chybně označených jako „passed“, což měnilo i leaderboard pořadí. Další práce ukázala průměrné nafouknutí resolve rate o 6,4 absolutního bodu a benchmark mutation studie ukazují, že formální issue prompty umí u některých modelů přestřelit reálnou interaktivní schopnost o více než 50 %. Brát leaderboard jako ground truth je prostě trash hodnocení. JEFF nesmí optimalizovat jen na statický SWE-bench Verified. citeturn11search5turn23search10turn23search1turn23search18turn23search6

Self-improving coding agents jsou dnes hlavně benchmarkové stroje, ne operator-trustworthy systémy. SICA ukazuje autonomní self-editing scaffoldu a růst výkonu na subsetu SWE-bench Verified. Darwin Gödel Machine buduje archiv agentů a přijímá mutace podle benchmarkové validace. Live-SWE-agent jde ještě dál a za běhu přepisuje vlastní scaffold. To je výzkumně skvělé. Produktově je to ale pořád problematické: outer loop sice používá explicitní evaluator, ale ten evaluator je zpravidla benchmark score, ne dlouhodobá pravdivost stavu, ani bezpečný přechod truth mutation v konkrétním repositáři. Pro JEFF je to inspirace pro offline scaffold search, ne pro online důvěryhodnou exekuci. citeturn8search0turn9search0turn8search6

Reviewer- a verifier-based agenty je nutné držet na krátkém vodítku. OpenHands critic je zajímavý přes early stopping a reranking, R4P je rychlý patch verifier a SpecRover reviewer umí dávat důkazový materiál k patchi. Jenže právě OpenHands veřejně ukázal, že benchmark-only critics jsou na reálných produkčních outcome proxys téměř náhodné. Z toho plyne jednoduché pravidlo: modelový reviewer je dobrý jako **prefilter**, **reranker** nebo **escalation signal**; jako finální accept/reject gate je slabý, pokud před ním neprojdou tvrdé deterministické checky. citeturn31search1turn28view1turn22search0turn22search1

## What JEFF should actually implement

JEFF by neměl implementovat „autonomního vývojáře“. To je špatně položený cíl. Měl by implementovat **truthful, bounded, evaluator-first software engineering runtime**, protože to je přesně ta mezera, kterou většina současných harnessů neřeší dobře. A paradoxně už na to má správný skelet: persisted runtime, bounded `/run`, approval-gated continuation, explicitní inspect/show/selection surfaces a rozlišení retry/recover/revalidate v operator contractu. citeturn12view0turn13view0

První věc, kterou má JEFF udělat, je udělat z evaluace samostatný stavový objekt, ne přílepek k exekuci. Každý běh musí vracet minimálně čtyři oddělené vrstvy: **execution outcome** (co se technicky spustilo), **artifact outcome** (jaký diff / log / report vznikl), **evaluation outcome** (které deterministické brány prošly a které ne), a **task posture** (splněno / částečně / nejasné / selhání / vyžaduje schválení). UTBoost a další práce na SWE-bench ukazují přesně proč: „testy prošly“ není nutně „issue je opravené“. citeturn23search1turn23search18turn11search5

Druhá věc je zavést **vrstvený evaluátor stack**, kde modelový optimismus přichází až po deterministice. Minimální rozumné vrstvy jsou: patch applies cleanly; reproducer fail-before/pass-after, pokud lze; targeted tests; lint/type/static analysis; smoke build nebo start aplikace; širší regresní canary; teprve potom reviewer/verifier model a nakonec člověk. To není přepjatý formalismus. Je to přímá syntéza toho, co funguje u Agentless, AutoCodeRover, aideru a toho, co velcí produktoví vendori stejně doporučují přes hooks, AGENTS.md a test workflows. citeturn17search3turn16search0turn34view0turn36view5turn38view1

Třetí věc: **retry nesmí být jen další prompt**. Retry musí mít typ a trigger. JEFF už má v kontraktu retry, recover a revalidate; to je správně. Doporučený trigger model je prostý: stejné plánování opravuj maximálně dvakrát, při opakovaném stejném failure signature vynuceně replan jednou, při environmentální nebo stavové nekonzistenci recover/rollback, při chybějícím evaluatoru nebo vysokém riziku rovnou approval_required či escalate. mini-SWE-agent, SWE-agent a OpenHands ukazují, že boundedness musí být explicitní v runtime limitech a iteration caps, ne schovaný v promptu. citeturn25view0turn26view0turn28view2turn30view0turn13view0

Čtvrtá věc: **approval boundary musí být silnější než selection boundary**. Výběr návrhu není povolení ke změně truth/stavu. Claude Code plan mode a Codex approval/sandbox split jsou tady velmi dobré vzory. JEFF by měl trvat na samostatném governance kroku před čímkoli, co překračuje diff budget, mění schéma, instaluje balíčky, sahá na secrets/infra, nebo mutuje canonical truth. Tohle je přesně místo, kde většina agentů dělá architektonickou prasárnu a vydává „navrhl jsem to“ za „můžu to udělat“. citeturn38view3turn36view1turn36view2turn13view0

Pátá věc: **recover musí být mechanický, ne narativní**. aider má `/undo`, Claude Code má checkpointing a rewind, Codex tlačí patch-based a review-based workflow. JEFF potřebuje podobně tvrdý recovery surface: git-based revert nebo workspace snapshot restore jako první třídu runtime, se samostatným outcome typem. Bez toho se „recover“ snadno zvrhne na trapné „zkusili jsme to znovu a doufáme“. citeturn33view1turn38view2turn37search3

Šestá věc: **operator-facing status musí být doslova pravdivý a nudný**. Žádné „done“, pokud prošel jen příkaz. Žádné „fixed“, pokud prošel jen smoke test. Žádné „verified“, pokud verdict nese jen critic. Místo toho stavy jako `executed_but_unverified`, `verified_on_targeted_checks_only`, `regression_risk_detected`, `approval_required_for_truth_mutation`, `inconclusive_missing_evaluator`, `recoverable_env_failure`. Právě tohle oddělení JEFF ve svém README a contractu už naznačuje; teď ho musí dotáhnout až do coding loopu. citeturn12view0turn13view0turn31search1

Sedmá věc: **benchmark harness držet odděleně od operator harnessu**. OpenHands evaluation harness je užitečný, ale jeho `user_response_fn` je benchmarkové lepidlo, ne pravdivé UX. JEFF by měl mít oddělený batch runner pro benchmarky a oddělený operator runtime pro skutečnou práci. Pokud to smíchá, skončí u benchmark theater, ne u důvěryhodné architektury. citeturn30view0turn23search6turn10search1

## Návrh kódovacího vzoru pro JEFF

Následující návrh je syntéza nejsilnějších patternů z mini-SWE-agent, Agentless, AutoCodeRover, aideru, OpenHands, Claude Code a Codexu, ale přepsaná do JEFFovy boundary-first filozofie. citeturn25view0turn17search3turn16search0turn34view0turn28view3turn38view3turn36view1

**Task intake.** Přijmi úkol jen jako claim, ne jako pravdu. Zapiš scope, risk class, očekávaný evaluator contract a diff budget.

**Truth/context read.** Udělej immutable snapshot repa, branch, commit SHA, konfigurace evaluatoru, dostupných test příkazů a provozních omezení. Pokud evaluator contract chybí, status je hned `inconclusive_missing_evaluator`, ne „let’s vibe“.

**Proposal.** Vygeneruj jeden nebo více návrhů řešení, ale bez mutace truth. Každý návrh musí obsahovat očekávané soubory, odhadovaný typ změny, plán validace a předpokládané riziko.

**Selection.** Vyber návrh nebo nech operátora vybrat. Výběr neznamená povolení.

**Action formation.** Rozpadni vybraný návrh na malé change sets. Každý change set musí mít cíl, očekávaný check a rollback anchor.

**Governance.** Pokud change set překračuje risk policy, čeká na approval. Typicky: package install, migrations, infra, secrets, networked tooling, diff rozsah nad limit, změna evaluator stacku.

**Execution.** Proveď edit v sandboxu nebo na pracovní větvi. Výstupem není ještě „úspěch“, ale jen artifact set: diff, logy, stdout/stderr, exit codes, modified files, side effects.

**Outcome normalization.** Normalizuj technické výsledky do jednotného modelu: `execution_success`, `execution_failure`, `no_effect`, `partial_effect`, `unexpected_side_effect`, `env_failure`.

**Evaluation.** Spusť pevný evaluator stack v tomto pořadí:  
A. patch/editor sanity;  
B. fail-before/pass-after reproducer, pokud je bug fix;  
C. targeted testy na dotčené moduly;  
D. lint / type / static analysis;  
E. smoke build nebo runtime start;  
F. širší regression subset;  
G. reviewer/verifier vrstva jako doplněk, ne primární gate;  
H. human review pro truth mutation.  
Pokud A–F nejsou dostupné, verdict nesmí být `verified`; maximálně `proposed_with_weak_evidence`. citeturn16search0turn17search3turn34view0turn38view1turn31search1turn22search0

**Retry / revalidate / recover / escalate.**  
Stejný plán: nejvýš 2 opravné iterace.  
Replan: nejvýš 1× po opakovaném stejném failure signature nebo nulovém progresu.  
Recover: 1× mechanickým rollbackem na checkpoint / git anchor.  
Escalate: okamžitě při chybějícím evaluatoru, nekonzistentním stavu, překročení budgetu, nebo pokud reviewer/model signal odporuje deterministickým checkům. Deterministika má vždy přednost.

**Transition.** Pravdu mutuj až po splnění mandatory gates a případném approval. Memory zapisuj odděleně od truth mutation a jen s provenance.

Doporučené **failure classes** pro JEFF jsou: `tool_error`, `env_error`, `parse_error`, `blocked_by_policy`, `no_progress`, `reproducer_failed_to_reproduce`, `targeted_checks_failed`, `regression_detected`, `weak_evidence_only`, `human_rejected`, `verified_partial_only`, `ready_for_transition`.

Doporučené **stop conditions** jsou: všechny mandatory gates prošly; opakovaný stejný failure signature; nulový měřitelný progres přes dvě iterace; budget/time cap; chybějící evaluator; explicitní operátorský reject; nebo rozpor mezi artifact truth a claimed success.

## Doporučení podle priority

Priority níže jsou záměrně tvrdé. Jsou seřazené podle toho, co JEFFu reálně zvýší důvěryhodnost a co je naopak architektonický odpad.

**Top 10 věcí, které má JEFF převzít**

1. Tvrdé deterministické brány nad každou mutací kódu.  
2. Reproducer-first politiku pro bug-fixing.  
3. Oddělení planneru s read-only režimem od execution agenta s write právem.  
4. Git/checkpoint rollback jako první třídu runtime.  
5. Explicitní retry/replan/recover stavy, ne volný text v promptu.  
6. Trajektorie a audit surfaces pro každý pokus.  
7. Odděleného reviewer/verifier agenta pouze jako doplněk po testech.  
8. Repo-level contract file s příkazy build/test/lint/typecheck a risk policy.  
9. Approval boundary oddělenou od selection boundary.  
10. Samostatný benchmark harness mimo operátorský runtime. citeturn16search0turn17search3turn28view3turn33view1turn38view2turn26view0turn28view1turn13view0turn30view0

**Top 10 věcí, které má JEFF odmítnout**

1. Modelové confidence jako náhradu verifikace.  
2. „Vybral jsem návrh“ jako náhradu povolení.  
3. „Příkaz doběhl“ jako náhradu skutečného task success.  
4. Multi-agent divadlo bez tvrdých rolových bran.  
5. Nekonečné retry bez failure taxonomy.  
6. Benchmark score jako hlavní pravdu o produkční kvalitě.  
7. Kritika/reviewer model jako jediný accept/reject gate.  
8. Logy a artefakty jako náhradu canonical truth.  
9. State mutation bez rollback anchoru.  
10. Statický SWE-bench jako jediný eval cíl. citeturn31search1turn23search1turn23search6turn23search18turn13view0

**Top 5 systémů, které stojí za hluboké studium**

mini-SWE-agent, Agentless, AutoCodeRover, OpenHands SDK a aider. První tři kvůli poctivé evaluační kostře, OpenHands kvůli composable SDK a verifier experimentům, aider kvůli nejlepší praktické rollback/test disciplíně. citeturn25view0turn17search3turn16search0turn28view0turn34view0

**Top 3 repozitáře, proti nimž má smysl rychle prototypovat JEFFův harness**

`SWE-agent/mini-swe-agent` jako referenční minimum kontrolního toku; `OpenHands/OpenHands` jako referenční maximum kompozice a evaluator surfaces; `Aider-AI/aider` jako referenční minimum důvěryhodného interaktivního workflow s rollbackem. To nejsou „nejlepší agenty“. Jsou to nejlepší kontrastní studijní materiály. citeturn7search1turn28view0turn35view0

**Top 3 benchmark/eval harnessy, které má JEFF používat**

SWE-bench Verified přes `sb-cli` jako základní reprodukovatelný patch-based grader; SWE-bench-Live jako test na čerstvost a odolnost proti kontaminaci; EvoClaw jako test dlouhodobé kontinuální evoluce místo jednorázových issue fixů. Pokud bude kapacita navíc, Terminal-Bench je dobrý čtvrtý kandidát pro terminal-grounded úlohy mimo čisté bug-fixing. citeturn11search0turn11search5turn23search10turn10search1turn10search5turn10search13turn10search2turn10search6turn10search10turn10search3