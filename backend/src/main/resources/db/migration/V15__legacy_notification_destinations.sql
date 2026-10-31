UPDATE user_notification SET link=CONCAT(link,'?focus=',message_id) WHERE kind='CHAT' AND message_id IS NOT NULL AND link REGEXP '^/messages/[0-9]+$';
UPDATE user_notification n JOIN (
 SELECT old.id,MIN(c.id) AS reply_id
 FROM user_notification old
 JOIN place_comment c ON c.root_id=CAST(SUBSTRING_INDEX(old.link,'/',-1) AS UNSIGNED) AND c.place_id=CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(old.link,'/',3),'/',-1) AS UNSIGNED)
 JOIN place_comment p ON p.id=c.parent_id AND p.user_id=old.user_id
 WHERE old.kind='REPLY' AND old.link REGEXP '^/campus/[0-9]+/conversations/[0-9]+$'
 AND ABS(TIMESTAMPDIFF(SECOND,c.created_at,old.created_at))<=2
 GROUP BY old.id HAVING COUNT(*)=1
) matched ON matched.id=n.id SET n.message_id=matched.reply_id,n.link=CONCAT(n.link,'?focus=',matched.reply_id);
