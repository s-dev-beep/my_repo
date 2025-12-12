import Link from 'next/link'
import { Building2, ArrowLeft } from 'lucide-react'

export default function CookiePolicyPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="inline-flex items-center space-x-2">
            <Building2 className="h-6 w-6 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">Dynamic CRM</span>
          </Link>
        </div>
      </div>

      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Link>

        <h1 className="text-4xl font-bold text-gray-900 mb-4">Cookie Policy</h1>
        <p className="text-gray-600 mb-8">Last updated: {new Date().toLocaleDateString()}</p>

        <div className="prose prose-blue max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">1. What Are Cookies</h2>
            <p className="text-gray-700 leading-relaxed">
              Cookies are small pieces of text sent to your web browser by a website you visit. A cookie file 
              is stored in your web browser and allows the service or a third-party to recognize you and make 
              your next visit easier and the service more useful to you.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">2. How We Use Cookies</h2>
            <p className="text-gray-700 leading-relaxed mb-3">
              When you use and access Dynamic CRM, we may place a number of cookie files in your web browser. 
              We use cookies for the following purposes:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>To enable certain functions of the service</li>
              <li>To provide analytics and usage statistics</li>
              <li>To store your preferences and settings</li>
              <li>To enable advertisements delivery, including behavioral advertising</li>
              <li>To authenticate users and prevent fraudulent use</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Types of Cookies We Use</h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Essential Cookies</h3>
                <p className="text-gray-700 leading-relaxed">
                  These cookies are necessary for the website to function properly. They enable core functionality 
                  such as security, network management, and accessibility. You may disable these by changing your 
                  browser settings, but this may affect how the website functions.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Analytics Cookies</h3>
                <p className="text-gray-700 leading-relaxed">
                  These cookies help us understand how visitors interact with our website by collecting and 
                  reporting information anonymously. This helps us improve our service and user experience.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Functional Cookies</h3>
                <p className="text-gray-700 leading-relaxed">
                  These cookies enable the website to provide enhanced functionality and personalization. They may 
                  be set by us or by third-party providers whose services we have added to our pages.
                </p>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Marketing Cookies</h3>
                <p className="text-gray-700 leading-relaxed">
                  These cookies are used to track visitors across websites. The intention is to display ads that 
                  are relevant and engaging for the individual user and thereby more valuable for publishers and 
                  third-party advertisers.
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Third-Party Cookies</h2>
            <p className="text-gray-700 leading-relaxed mb-3">
              In addition to our own cookies, we may also use various third-party cookies to report usage 
              statistics of the service and deliver advertisements on and through the service. These include:
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
              <li>Google Analytics for website analytics</li>
              <li>Google Maps for location services</li>
              <li>Social media platforms for social sharing features</li>
              <li>Advertising networks for personalized advertising</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Managing Cookies</h2>
            <p className="text-gray-700 leading-relaxed mb-3">
              You can control and/or delete cookies as you wish. You can delete all cookies that are already on 
              your computer and you can set most browsers to prevent them from being placed. If you do this, 
              however, you may have to manually adjust some preferences every time you visit a site and some 
              services and functionalities may not work.
            </p>
            <p className="text-gray-700 leading-relaxed">
              To learn more about how to manage cookies, visit{' '}
              <a href="https://www.allaboutcookies.org" target="_blank" rel="noopener noreferrer" 
                 className="text-blue-600 hover:underline">
                www.allaboutcookies.org
              </a>
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Your Consent</h2>
            <p className="text-gray-700 leading-relaxed">
              By using our website, you consent to our use of cookies in accordance with this Cookie Policy. 
              If you do not agree to our use of cookies, you should set your browser settings accordingly or 
              not use our website.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Changes to This Policy</h2>
            <p className="text-gray-700 leading-relaxed">
              We may update our Cookie Policy from time to time. We will notify you of any changes by posting 
              the new Cookie Policy on this page and updating the "Last updated" date.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Contact Us</h2>
            <p className="text-gray-700 leading-relaxed">
              If you have any questions about our use of cookies, please contact us:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg mt-3">
              <p className="text-gray-700">
                <strong>Email:</strong> privacy@dynamiccrm.com<br />
                <strong>Phone:</strong> +90 555 123 45 67<br />
                <strong>Address:</strong> Istanbul, Turkey
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
