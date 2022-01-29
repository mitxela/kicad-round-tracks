#!/bin/bash -e

version=$(git describe --tags --dirty)
name=$(echo kicad-round-tracks-$version.zip)

echo "Building release $version"
cp metadata.json.template metadata.json
sed -i -e "s/VERSION/$version/g" metadata.json
sed -i '/download_/d' metadata.json
sed -i '/install_size/d' metadata.json

mkdir resources
cp icon.png resources/

mkdir plugins
cp *.py plugins/
cp round_tracks.png plugins/

zip -r $name plugins resources metadata.json

rm -rf plugins
rm -rf resources

sha=$(sha256sum $name | cut -d' ' -f1)
size=$(du -b $name | cut -f1)
installSize=$(unzip -l $name | tail -1 | xargs | cut -d' ' -f1)

cp metadata.json.template metadata.json
sed -i -e "s/VERSION/$version/g" metadata.json
sed -i -e "s/SHA256/$sha/g" metadata.json
sed -i -e "s/DOWNLOAD_SIZE/$size/g" metadata.json
sed -i -e "s/INSTALL_SIZE/$installSize/g" metadata.json

ls -lh $name metadata.json

