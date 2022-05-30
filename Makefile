dev:
	$(MAKE) build
	echo "Starting dev server..."
	docker-compose up

build:
	echo "Building..."
	cd dashboard; npm run build
	docker build -t beacon-server:dev .
	echo "Done!"

release:
	$(MAKE) build
	docker tag beacon-server:dev $(tag)
	docker push $(tag)
