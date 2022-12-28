include jengaconfig

sdf-wineguard-dev-image:
	docker build -t $(WINEGUARD_TEST_IMAGE) -f $(SDF_WINEGUARD_DEV_DOCKERFILE) ./SoftwareDefinedFarm

sdf-wineguard-test-image:
	docker build -t $(WINEGUARD_UPSTREAM_IMAGE) -f $(SDF_WINEGUARD_DOCKERFILE) ./SoftwareDefinedFarm


default: sdf-wineguard-dev-image 
