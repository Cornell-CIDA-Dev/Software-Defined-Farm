include jengaconfig

sdf-wineguard-dev-image:
	docker build -t $(OPEN_WINEGUARD_DEV_IMAGE) -f $(SDF_WINEGUARD_DEV_DOCKERFILE) ./SoftwareDefinedFarm

sdf-wineguard-test-image:
	docker build -t $(OPEN_WINEGUARD_UPSTREAM_IMAGE) -f $(SDF_WINEGUARD_DOCKERFILE) ./SoftwareDefinedFarm


# Build a compute module to be run in a kubestellar cluster
sdf-wineguard-compute-dev-image:
	docker build -t $(OPEN_WINEGUARD_COMPUTE_DEV_IMG) -f $(SDF_WINEGUARD_COMPUTEDEV_DOCKERFILE) ./SoftwareDefinedFarm

# Build a trainer to be run in a container
sdf-wineguard-trainer-dev-image:
	docker build -t $(OPEN_WINEGUARD_TRAINER_DEV_IMG) -f $(SDF_WINEGUARD_TRAINERDEV_DOCKERFILE) ./SoftwareDefinedFarm

# Build a trainer to be run in a kubestellar cluster
sdf-wineguard-trainer-ks-image:
	docker build -t $(OPEN_WINEGUARD_TRAINER_KS_IMG) -f $(SDF_WINEGUARD_TRAINER_KS_DOCKERFILE) ./SoftwareDefinedFarm

# Build the sharpening cloud modules to be tested in a container
sdf-sharpening-cloud-dev-image:
	docker build -t $(OPEN_SHARPENING_CLOUD_DEV_IMG) -f $(SDF_SHARPENING_CLOUDDEV_DOCKERFILE) ./SoftwareDefinedFarm

# Build the sharpening cloud modules to be tested in a kubestellar container
sdf-sharpening-cloud-ks-image:
	docker buildx build  --platform linux/amd64,linux/arm64,linux/arm/v7 -t $(OPEN_SHARPENING_CLOUD_UPSTREAM_IMG) --push -f $(SDF_SHARPENING_CLOUD_UPSTREAM_DOCKERFILE) ./SoftwareDefinedFarm

sdf-dairymanager-dev-image:
	docker build -t $(OPEN_DAIRYMGR_DEV_IMAGE) -f $(SDF_DAIRYMGR_DEV_DOCKERFILE) ./SoftwareDefinedFarm

sdf-dairymanager-test-image:
	docker build -t $(OPEN_DAIRYMGR_TEST_IMAGE) -f $(SDF_DAIRYMGR_DOCKERFILE) ./SoftwareDefinedFarm

sdf-two-dev-image:
	docker build -t $(OPEN_SDF_TWO_DEV_IMAGE) -f $(SDF_TWO_DEV_DOCKERFILE) ./SoftwareDefinedFarm

default: sdf-wineguard-dev-image
