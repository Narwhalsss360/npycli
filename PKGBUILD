_name=npycli
pkgname=python-$_name
pkgver=0.5.0
pkgrel=1
pkgdesc='Python CLI builder package'
arch=('any')
url='https://github.com/Narwhalsss360/npycli'
license=('MIT')
makedepends=(python-build python-installer python-wheel python-setuptools python-setuptools-scm)

build() {
    cd ..
    branch=$(git branch --show-current)
    if [ $branch != "pkgbuild" ]; then
        echo "ERROR: Expected npycli pkgbuild git branch" >&2
        exit 1
    fi

    python -m build --wheel --no-isolation
}

package() {
    cd ..
    branch=$(git branch --show-current)
    if [ $branch != "pkgbuild" ]; then
        echo "ERROR: Expected npycli pkgbuild git branch" >&2
        exit 1
    fi

    python -m installer --destdir="$pkgdir" dist/*.whl
}
