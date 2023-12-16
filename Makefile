rm-container:
	-docker rm tcc_container

clean: rm-container
	-docker image rm tcc_image

build: clean
	docker build . -t tcc_image --rm

run: rm-container
	docker run --name tcc_container -v ${PWD}/src:/home/daniel/tcc -e GRANT_SUDO=yes --user root -p 8888:8888 tcc_image

buid-run: build run

start: 
	docker start -i tcc_container
