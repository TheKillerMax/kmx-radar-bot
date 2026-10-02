# Seguridad

- Nunca abras issues, commits o capturas que contengan `INSTAGRAM_ACCESS_TOKEN`, la clave secreta de Meta o `TOKEN_ENCRYPTION_PASSWORD`.
- El repositorio está pensado para ser público, por lo que todos los secretos deben vivir en GitHub Actions Secrets.
- `data/instagram_token.enc` puede ser público porque está cifrado; su seguridad depende de mantener en secreto `TOKEN_ENCRYPTION_PASSWORD`.
- Si un token aparece accidentalmente en un commit, revócalo/regénéralo en Meta de inmediato. Borrarlo del último commit no basta porque puede permanecer en el historial.
- Usa autenticación en dos pasos para GitHub, Instagram y Meta.
