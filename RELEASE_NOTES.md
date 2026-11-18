# Assembly Editor 5.5.7

- CyberFirePulse-setupicoon en bestaande wizardafbeeldingen toegevoegd.
- Eigen ASM-chipicoon toegevoegd aan de Windows-app, vensters en snelkoppelingen.
- Optionele bureaubladsnelkoppeling en Nederlandse/Engelse installer toegevoegd.

- Vraagt om opslaan voordat Nieuw, Openen, voorbeeld laden of Afsluiten de code vervangt.
- Opslaan gebruikt een tijdelijk bestand. Annuleren en opslagfouten behouden het document.
- Een mislukte build wist de vorige uitvoerselectie.
- Run bouwt opnieuw als bron of doelplatform gewijzigd is.
- Build en ROP/JOP werken op de achtergrond met time-outs voor externe opdrachten.
- Venstertitel en Help noemen 5.5.7.
- Hulpmiddelen worden automatisch gevonden, persoonlijke instellingen worden per gebruiker opgeslagen.
- Broncodebundel, installatiehandleiding, afhankelijkhedenlijst en Windows-installer toegevoegd.
- Eigen gebruiksvoorwaarden met alle rechten voorbehouden, zoals gekozen voor deze release.

## Validatie

Windows-consolebuild en uitvoering geslaagd met correcte voorbeeldtekst.
Windows-GUI-build geslaagd. Documentannulering, opslaan, instellingen,
buildfouten, achtergrondtaken, time-outafhandeling en PE-hardening gecontroleerd.
De verpakte Windows-app bleef bij de opstartcontrole actief.
De overdracht van ROP/JOP-resultaten is met gesimuleerde analyse getest.
Linux, een volledige live ROP/JOP-scan en de installerinstallatie zijn nog niet getest.
