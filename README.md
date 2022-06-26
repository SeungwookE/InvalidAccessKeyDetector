# InvalidAccessKeyDetector
invalide access key detector using aws cli

basically using two aws iam command

- aws iam get-users
- aws iam list-access-keys --user-name {userName}


**How to use?**

run 'start' script in the root. with valid_time argument like below.
(start 스크립트를 유효 시간 인자와 함께 커맨드라인으로 실행합니다.)

> ./start 3000  
> (Detect access keys older than 3000 hours after creation / 생성 후 3000 시간이 지난 access key 검출)

위 커맨드 실행의 결과로 동일한 프로젝트 root 내에 invalid_access_keys.txt 파일이 생성됩니다.


**Prerequisite**

1. To run this program, proper aws account access key and secret should be setup on the environment. 
2. run **./setup** script to install all prerequisite python libraries
