You can add specific code to the dumper of a content registering one or more
IExtensionDumper classes, use 'name' to avoid conflict.

For instance, take the PloneSiteDumper defined in oop.staticdump.dumpers.adapters,
you can add other 2 dumpers with:


    <adapter
      name="ertoolkit.plonedumper"
      factory=".adapters.PloneSiteDumper"
      provides="oops.staticdump.interfaces.IExtensionDumper"
      for="oops.staticdump.dumpers.adapters.PloneSiteDumper"
      permission="zope.Public"
      />

    <adapter
      name="ertoolkit.plonedumper1"
      factory=".adapters.PloneSiteDumper1"
      provides="oops.staticdump.interfaces.IExtensionDumper"
      for="oops.staticdump.dumpers.adapters.PloneSiteDumper"
      permission="zope.Public"
      />
