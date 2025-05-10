Dette er koden inklusiv kommentar til projekt "PixelWipe" i anledning af programmering (B) eksamen, sommer 2025. 
Lavet af gruppen bestående af Nikolaj N. og Sigurd H. - V3x.

PixelWipe er lavet til at løse et simpelt problem, som vi selv har oplevet når vi har skulle bruge billeder til en rapport, PowerPoint, eller lignende. Et simpelt lille program, som kan fjerne baggrunden og samtidig konvertere ens billede til et PNG med alpha baggrund (gennemsigtig). 

Programmet kan håndtere enkelte filer, samt mapper, med følgende formater: 
- PNG
- JPG
- JPEG
- WEBP
- AVIF

Billede af programmets brugerflade:
![image](https://github.com/user-attachments/assets/5b2a85c0-a696-4485-98e5-7fd75c08dd13)
_*Xiaomi SU7 Ultra_


**De vigtige libraries:**

Start med først at installere fra requirements.txt (Nogle IDE's kan finde ud af det automatisk, andre kræver en manuel kommando med pip) - hvis det fejler i hvilken som helst grad, er nedenstående en liste over de vigtigste libraries:
- rembg
- pillow
- pilliw_avif
- onnxruntime
- cryptography
- kivy

**Troubleshooting**

1. Hvis man i sin IDE ender med, at ens terminal giver numba violations i en uendelig lang kører, prøv at indsæt følgende linje under import os:

> os.environ["NUMBA_DISABLE_JIT"] = "1"
2. For at installere requirements.txt skal man bruge setuptools og pip. Disse er Python 3.12.X ikke født med, og skal derfor manuelt installeres. 
