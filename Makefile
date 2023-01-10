include jengaconfig

sdf-wineguard-dev-image:
	docker build -t $(OPEN_WINEGUARD_DEV_IMAGE) -f $(SDF_WINEGUARD_DEV_DOCKERFILE) ./SoftwareDefinedFarm

sdf-wineguard-test-image:
	docker build -t $(OPEN_WINEGUARD_UPSTREAM_IMAGE) -f $(SDF_WINEGUARD_DOCKERFILE) ./SoftwareDefinedFarm

sdf-dairymanager-dev-image:
	docker build -t $(OPEN_DAIRYMGR_DEV_IMAGE) -f $(SDF_DAIRYMGR_DEV_DOCKERFILE) ./SoftwareDefinedFarm

sdf-dairymanager-test-image:
	docker build -t $(OPEN_DAIRYMGR_TEST_IMAGE) -f $(SDF_DAIRYMGR_DOCKERFILE) ./SoftwareDefinedFarm

default: sdf-wineguard-dev-image
