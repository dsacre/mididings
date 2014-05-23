.. currentmodule:: mididings.extra


.. _extra-hooks:

:mod:`mididings.extra` Hooks
============================

Hooks extend the functionality of mididings.
Instances of these classes can be registered using the :func:`~.hook()`
function.


.. autoclass:: MemorizeScene
    :no-members:

.. autoclass:: mididings.extra.inotify.AutoRestart
    :no-members:

    Defined in :mod:`mididings.extra.inotify`.
    Requires `pyinotify <https://github.com/seb-m/pyinotify>`_.

.. autoclass:: mididings.extra.osc.OSCInterface
    :no-members:

    Defined in :mod:`mididings.extra.osc`.
    Requires `pyliblo <http://das.nasophon.de/pyliblo/>`_.
