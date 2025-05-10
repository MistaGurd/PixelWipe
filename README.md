Dette er koden inklusiv kommentar til projekt "PixelWipe" i anledning af programmering (B) eksamen, sommer 2025. 
Lavet af gruppen bestående af Nikolaj N. og Sigurd H. - V3x.

PixelWipe er lavet til at løse et simpelt problem, som vi selv oplever når vi har skulle bruge billeder til en rapport, PowerPoint, eller lignende. Et simpelt lille program, som kan fjerne baggrunden og samtidig konvertere ens billede til et PNG med alpha baggrund (gennemsigtig). 

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
- rembg
- pillow
- pilliw_avif
- onnxruntime
- cryptography
- kivy

**Troubleshooting**

Hvis man i sin IDE ender med, at ens terminal giver numba violations i en uendelig lang kører, prøv at indsæt følgende linje under import os:
os.environ["NUMBA_DISABLE_JIT"] = "1"
