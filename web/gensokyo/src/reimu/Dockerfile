FROM php:8.2-cli

WORKDIR /var/www/html

COPY upload.php .
COPY index.php .
COPY reimu.png .

RUN mkdir uploads \
 && chown -R www-data:www-data uploads

RUN echo "PETIR{touhou_is_life_a_fever_dream_of_danmaku_hell_where_reimu_casually_glides_through_impossible_bullet_curtains_marisa_steals_your_soul_with_master_spark_every_boss_theme_hijacks_your_brain_at_3am_and_gensokyo_becomes_home_as_you_dodge_pixel_perfection_patterns_with_pride_pain_and_absolute_devotion_to_the_art_of_not_getting_hit}" > /flag.txt

CMD ["php", "-S", "0.0.0.0:80", "-t", "/var/www/html"]
