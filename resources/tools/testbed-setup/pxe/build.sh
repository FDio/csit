# Clean
docker rm --force fdio_pxe
docker rmi fdio_pxe:v1

# Build
docker build --tag fdio_pxe:v1 .

# Run yul1
docker run \
    --rm \
    --name fdio_pxe \
    --net host fdio_pxe:v1 \
    -e "E_INT=$(ip -o -4 route show to default | awk '{print $5}')" \
    -e "E_ADD=$(hostname -I | awk '{print $1}')"

