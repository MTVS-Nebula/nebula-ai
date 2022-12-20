Nebula AI
=============
52hertz 메타버스 플랫폼의 AI를 실행/관리하는 K8s 입니다.<br>
K8s 로 Container 를 통해 조건에 맞게 AI 모델을 실행하고, user data 를 분석/학습하며 지속적인 AI 모델 발전을 만듭니다.<br>

### 아키텍처
- AWS EKS 기능으로 AI 기능을 배포하고 있습니다.
- [ ] K8s 기능으로 Data-PipeLine 을 구성하고 있습니다.
- [ ] CodeBuild / ArgoCD 를 이용해 EKS 서비스를 적용/배포 CI/CD

### 구현 목표
<b>AI 모델 이용의 최적화</b><br>
- Embadding AI 모델이 완전히 실행되기까지 5~15초의 시간이 소요됨
- 여러 이용자가 한 번에 해당 기능을 동작하면 속도/서비스 측면에서 무거워지는 문제가 있음
- Deployment-Controller 를 이용해 HPA 를 설정하여 Pod 별로 서비스를 제공함
- Load-Balancer 기능으로 서비스에 가용할 수 자원의 K8s Node 를 자동으로 이용함
<br><br>

<b>Data PipeLine 구성</b>
- 1번/시간 user data 를 분석 후 AI 모델의 추가 학습 진행
- CronJob-Controller 를 이용해 정시 마다(" 0 */1 * * * ") 자동으로 데이터를 학습 후 AI 모델을 발전
- Docker Image 버전 업데이트
<br><br>

### CI
CodeBuild(AWS) : Build 파일 패키징 시 테스트 자동화<br>

### CD
<b>EKS 서비스</b> <br>
- CodeBuild : Docker Image 를 만들어 Docker-hub 로 배포<br>
  - Build 성공 시 해당 이미지를 EKS에 적용하여 Pod Container 를 Rolling-Update<br>

<b>배포</b> <br>
- [ ] ArgoCD : manifest 파일을 통해 EKS 에서 Application-Load-Balancer / NodePort 서비스를 적용

### 개발환경
- Kubernetes
- Docker
- Flask
- PostgreSQL
- ArgoCD
- Python
- CLIP
- UMAP
- AWS
  - EKS
  - ALB
  - AutoScaling
  - CodeBuild
  - EC2
  - VPC / Subnet
  - etc ...
