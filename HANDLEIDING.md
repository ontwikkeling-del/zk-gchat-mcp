# Google Chat in Claude - Handleiding

Met deze tool kun je vanuit Claude Code direct in Google Chat meelezen en berichten sturen. Handig om snel te checken wat er speelt zonder te schakelen tussen vensters. Het installeren kost een paar minuten en hoeft maar een keer.

## Wat je nodig hebt

- Je @zwartekraai.nl account
- Claude Code op je computer

## Stap 1: De code ophalen

Heb je de repo nog niet? Clone hem. Heb je hem al? Doe even een pull zodat je de laatste versie hebt.

## Stap 2: De installer draaien

Open een terminal in de map `Overig/Tools/GoogleChatMCP` en draai het script voor jouw systeem:

- Windows: `.\install.ps1`
- Mac of Linux: `bash install.sh`

Het script regelt alles zelf: het installeert de tool en zet hem klaar in Claude.

## Stap 3: Inloggen

Tijdens de installatie opent je browser. Log in met je **@zwartekraai.nl** account en klik op toestaan. Daarna mag je het browservenster sluiten. Je hoeft dit maar een keer te doen.

## Stap 4: Klaar

Herstart Claude Code en je kunt aan de slag. Een paar voorbeelden van wat je kunt vragen:

- "Wat speelt er in #tech?"
- "Geef me de laatste berichten uit #devteam"
- "Stuur in #devteam dat de deploy klaar is"
- "Vraag in #algemeen wie er morgen op kantoor is"

Berichten die je via Claude stuurt komen vanuit jouw eigen account, met een klein robot-icoontje ervoor zodat collega's zien dat het via de tool ging.

## Werkt iets niet?

- Foutmelding tijdens installeren? Lees de melding rustig - het script vertelt wat er mis ging. Vaak helpt het om het script gewoon opnieuw te draaien.
- Opnieuw inloggen nodig? Draai `python -m zk_gchat_mcp setup` (of `python3` op Mac/Linux) en log opnieuw in.
- Kom je er niet uit? Tik even het tech-team aan, dan helpen we je verder.
