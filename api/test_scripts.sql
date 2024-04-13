explain
select *
from bank
where bank_name = 'Сбербанк';

explain
SELECT text_sentence.id, text_sentence.sentence
FROM text_sentence
WHERE text_sentence.id IN (SELECT text_result.text_sentence_id
                           FROM text_result
                           WHERE text_result.model_id = 1
                             AND text_result.is_processed = false);

explain
SELECT text_sentence.id
FROM text_sentence
         JOIN text ON text.id = text_sentence.text_id
         JOIN source ON source.id = text.source_id
         LEFT OUTER JOIN
     (SELECT text_result.id               AS id,
             text_result.text_sentence_id AS text_sentence_id,
             text_result.model_id         AS model_id,
             text_result.result           AS result,
             text_result.is_processed     AS is_processed
      FROM text_result
      WHERE text_result.model_id = 1) AS anon_1 ON text_sentence.id = anon_1.text_sentence_id
WHERE source.site IN ('bankri.ru', 'sravni.ru')
  AND anon_1.text_sentence_id IS NULL;

explain
select *
from text_sentence
where id in (1656336, 1656367, 165667, -1);

explain
select count(id)
from text_sentence; --16563367

SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'ix_text_sentence_text_id';


select
    id,
    model_name, source_type,
    --avg(case when total > 0 then ((positive - negative)::float)/total else 0 end) over (PARTITION BY model_name, source_type) as "index"
    avg(((positive - negative)::float)/total) over (PARTITION BY model_name, source_type) as "index"
from aggregate_table_model_result
order by id
limit 100;
