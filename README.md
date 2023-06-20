Nebula AI
=============
52 Hertz 메타버스 플랫폼의 AI를 실행/관리하는 Kubernetes입니다.<br>
Kubernetes로 Container를 통해 조건에 맞게 AI 모델을 실행하고, 이용자의 데이터를 분석/학습하며 지속적인 AI 모델의 발전을 만듭니다.<br>

<p align="center"><img src="https://user-images.githubusercontent.com/86669008/209777782-1f828229-a17e-4a9d-b580-46681d45c71c.jpg"/></p>

### 아키텍처
- AWS EKS 기능으로 AI 기능을 배포하고 있습니다.
- Kubernetes 기능으로 AI Infra를 구성하고 있습니다.

### 구현 목표
<b>AI 모델 이용의 최적화</b><br>
- Embedding AI 모델이 완전히 실행되기까지 5~15초의 시간 문제 해결
- 여러 이용자가 한 번에 해당 기능을 동작하면 속도/서비스 측면에서 경량화
- Deployment-Controller를 이용해 Pod 별로 서비스를 제공
- Load-Balancer를 통해 서비스에 가용할 수 자원의 Kubernetes Node를 자동으로 이용
<br><br>

<b>Scheduler</b>
- 1번/시간 user data 를 분석 후 AI 모델의 추가 학습 진행
- CronJob-Controller 를 이용해 정시 마다(" 0 */1 * * * ") 자동으로 데이터를 학습 후 AI 모델을 발전
<br><br>

<b>Embedding Update</b><br>
- 새로운 프로필이 생성(추가)될 때, 생성된 프로필에 해당하는 섬의 좌표에 대해서만 Embadding 실행
- 1번씩/시간 전체 섬에 대한 프로필 정보로 AI 모델에 fit_transform 하여 전체 섬에 대해 Embadding & Clustering 실행
<br><br>

### CI
AWS CodeBuild : Build 파일 패키징 시 테스트 자동화<br>

### CD
<b>EKS 서비스</b> <br>
- CodeBuild : Docker Image를 만들어 Dockerhub로 Push<br>
  - Build-Push 성공 시 해당 이미지를 EKS에 적용하여 Pod의 Container를 Rolling-Update<br>

<b>배포</b> <br>
- [ ] ArgoCD : Manifest 파일을 통해 EKS 에서 Application-Load-Balancer / NodePort 서비스를 적용

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
